from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping
from dataclasses import asdict, dataclass, replace
from enum import Enum
import hashlib
import hmac
import json
import math
from typing import Any

from .model import Verdict
from .replay import (
    ReplayBundle,
    ReplayMetrics,
    ReplayResult,
    calculate_replay_metrics,
    replay_case,
)


_HOLDOUT_REPORT_SCHEMA = "resonance.arbitrage.holdout-report/v0.2"
_SELECTION_RULE = (
    "calibration_only:truth_lower_bound>survival_lower_bound>truth_events>"
    "lower_indeterminate>overprediction_penalty>higher_execute_threshold"
)


def _canonical_json(payload: Any) -> str:
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def _sha256(payload: Any) -> str:
    return hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()


class HoldoutStatus(str, Enum):
    PASSED_HOLDOUT = "PASSED_HOLDOUT"
    INSUFFICIENT_CORPUS = "INSUFFICIENT_CORPUS"
    INSUFFICIENT_CALIBRATION = "INSUFFICIENT_CALIBRATION"
    NO_ELIGIBLE_CALIBRATION_POLICY = "NO_ELIGIBLE_CALIBRATION_POLICY"
    INSUFFICIENT_VALIDATION = "INSUFFICIENT_VALIDATION"
    VALIDATION_FAILED = "VALIDATION_FAILED"


class HoldoutSplitError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class HoldoutPolicy:
    validation_fraction: float
    min_calibration_operations: int
    min_validation_operations: int
    min_calibration_truth_events: int
    min_validation_truth_events: int
    min_truth_rate_lower_bound: float
    min_survival_rate_lower_bound: float
    confidence_z: float = 1.96

    def __post_init__(self) -> None:
        if not math.isfinite(self.validation_fraction) or not 0.0 < self.validation_fraction < 1.0:
            raise ValueError("validation_fraction must be finite and in (0, 1)")
        for name in (
            "min_calibration_operations",
            "min_validation_operations",
            "min_calibration_truth_events",
            "min_validation_truth_events",
        ):
            if getattr(self, name) < 1:
                raise ValueError(f"{name} must be >= 1")
        for name in (
            "min_truth_rate_lower_bound",
            "min_survival_rate_lower_bound",
        ):
            value = getattr(self, name)
            if not math.isfinite(value) or not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be finite and in [0, 1]")
        if not math.isfinite(self.confidence_z) or self.confidence_z < 0:
            raise ValueError("confidence_z must be finite and non-negative")


@dataclass(frozen=True, slots=True)
class PolicyCandidate:
    execute_net_edge_bps: float

    def __post_init__(self) -> None:
        if not math.isfinite(self.execute_net_edge_bps) or self.execute_net_edge_bps <= 0:
            raise ValueError("execute_net_edge_bps must be finite and positive")

    def to_payload(self) -> dict[str, float]:
        return {"execute_net_edge_bps": self.execute_net_edge_bps}


@dataclass(frozen=True, slots=True)
class CandidateGrid:
    execute_net_edge_bps: tuple[float, ...]

    def __post_init__(self) -> None:
        execute = tuple(sorted(set(self.execute_net_edge_bps)))
        object.__setattr__(self, "execute_net_edge_bps", execute)
        if not execute:
            raise ValueError("candidate grid must be non-empty")
        for value in execute:
            if not math.isfinite(value) or value <= 0:
                raise ValueError("execute threshold grid values must be finite and positive")

    def candidates(self) -> tuple[PolicyCandidate, ...]:
        return tuple(PolicyCandidate(execute_net_edge_bps=value) for value in self.execute_net_edge_bps)

    def to_payload(self) -> dict[str, list[float]]:
        return {"execute_net_edge_bps": list(self.execute_net_edge_bps)}


def wilson_lower_bound(successes: int, total: int, *, z: float = 1.96) -> float | None:
    if successes < 0 or total < 0 or successes > total:
        raise ValueError("Wilson counts are invalid")
    if not math.isfinite(z) or z < 0:
        raise ValueError("Wilson z must be finite and non-negative")
    if total == 0:
        return None
    p = successes / total
    z2 = z * z
    denominator = 1.0 + z2 / total
    center = p + z2 / (2.0 * total)
    margin = z * math.sqrt((p * (1.0 - p) + z2 / (4.0 * total)) / total)
    return max(0.0, min(1.0, (center - margin) / denominator))


@dataclass(frozen=True, slots=True)
class PolicyEvaluation:
    candidate: PolicyCandidate
    metrics: ReplayMetrics
    execute_sim_count: int
    truth_events: int
    survival_events: int
    truth_rate_lower_bound: float | None
    survival_rate_lower_bound: float | None
    overprediction_penalty_bps: float
    results_sha256: str
    eligible: bool
    reasons: tuple[str, ...]

    def to_payload(self) -> dict[str, Any]:
        return {
            "candidate": self.candidate.to_payload(),
            "metrics": self.metrics.to_payload(),
            "execute_sim_count": self.execute_sim_count,
            "truth_events": self.truth_events,
            "survival_events": self.survival_events,
            "truth_rate_lower_bound": self.truth_rate_lower_bound,
            "survival_rate_lower_bound": self.survival_rate_lower_bound,
            "overprediction_penalty_bps": self.overprediction_penalty_bps,
            "results_sha256": self.results_sha256,
            "eligible": self.eligible,
            "reasons": list(self.reasons),
        }


@dataclass(frozen=True, slots=True)
class HoldoutSplitSummary:
    calibration_bundle_sha256: str
    validation_bundle_sha256: str
    calibration_operation_ids: tuple[str, ...]
    validation_operation_ids: tuple[str, ...]
    calibration_max_detected_at_ms: int
    validation_min_detected_at_ms: int

    def to_payload(self) -> dict[str, Any]:
        return {
            "calibration_bundle_sha256": self.calibration_bundle_sha256,
            "validation_bundle_sha256": self.validation_bundle_sha256,
            "calibration_operation_ids": list(self.calibration_operation_ids),
            "validation_operation_ids": list(self.validation_operation_ids),
            "calibration_max_detected_at_ms": self.calibration_max_detected_at_ms,
            "validation_min_detected_at_ms": self.validation_min_detected_at_ms,
        }


@dataclass(frozen=True, slots=True)
class HoldoutSplit:
    calibration: ReplayBundle
    validation: ReplayBundle
    summary: HoldoutSplitSummary

    def __post_init__(self) -> None:
        calibration_ids = {case.logical_operation_id for case in self.calibration.cases}
        validation_ids = {case.logical_operation_id for case in self.validation.cases}
        if calibration_ids & validation_ids:
            raise ValueError("logical operation leaked across holdout split")
        if self.summary.calibration_max_detected_at_ms >= self.summary.validation_min_detected_at_ms:
            raise ValueError("chronological holdout validation must be strictly later")


def _operation_groups(bundle: ReplayBundle) -> list[tuple[int, str, tuple[Any, ...]]]:
    grouped: dict[str, list[Any]] = defaultdict(list)
    for case in bundle.cases:
        grouped[case.logical_operation_id].append(case)
    rows: list[tuple[int, str, tuple[Any, ...]]] = []
    for operation_id, cases in grouped.items():
        ordered = tuple(sorted(cases, key=lambda case: case.attempt))
        detected_at = ordered[0].detected_at_ms
        if any(case.detected_at_ms != detected_at for case in ordered):
            raise ValueError("logical operation detection time drifted")
        rows.append((detected_at, operation_id, ordered))
    rows.sort(key=lambda row: (row[0], row[1]))
    return rows


def split_replay_bundle(bundle: ReplayBundle, policy: HoldoutPolicy) -> HoldoutSplit:
    rows = _operation_groups(bundle)
    total = len(rows)
    required = policy.min_calibration_operations + policy.min_validation_operations
    if total < required:
        raise HoldoutSplitError(
            f"insufficient logical operations for holdout split: {total} < {required}"
        )

    desired_validation = max(
        policy.min_validation_operations,
        math.ceil(total * policy.validation_fraction),
    )
    desired_validation = min(desired_validation, total - policy.min_calibration_operations)

    valid_cuts: list[int] = []
    for cut in range(policy.min_calibration_operations, total - policy.min_validation_operations + 1):
        if rows[cut - 1][0] < rows[cut][0]:
            valid_cuts.append(cut)
    if not valid_cuts:
        raise HoldoutSplitError(
            "no strict chronological boundary satisfies holdout minimums"
        )

    cut = min(valid_cuts, key=lambda value: (abs((total - value) - desired_validation), value))
    calibration_ids = {row[1] for row in rows[:cut]}
    validation_ids = {row[1] for row in rows[cut:]}
    calibration_cases = tuple(
        case for case in bundle.cases if case.logical_operation_id in calibration_ids
    )
    validation_cases = tuple(
        case for case in bundle.cases if case.logical_operation_id in validation_ids
    )
    calibration = ReplayBundle(cases=calibration_cases)
    validation = ReplayBundle(cases=validation_cases)
    summary = HoldoutSplitSummary(
        calibration_bundle_sha256=calibration.sha256,
        validation_bundle_sha256=validation.sha256,
        calibration_operation_ids=tuple(row[1] for row in rows[:cut]),
        validation_operation_ids=tuple(row[1] for row in rows[cut:]),
        calibration_max_detected_at_ms=rows[cut - 1][0],
        validation_min_detected_at_ms=rows[cut][0],
    )
    return HoldoutSplit(calibration=calibration, validation=validation, summary=summary)


def _case_window_policy_payload(case: Any) -> dict[str, Any]:
    policies = {
        _canonical_json(asdict(window.policy)): asdict(window.policy)
        for window in case.windows_by_market.values()
    }
    if not policies:
        raise ValueError("holdout case has no rolling-window policy context")
    if len(policies) != 1:
        raise ValueError("rolling-window policy drifted within replay case")
    return next(iter(policies.values()))


def _policy_context_payload(case: Any) -> dict[str, Any]:
    engine = asdict(case.engine_policy)
    engine.pop("execute_net_edge")
    return {
        "engine_policy": engine,
        "regime_policy": asdict(case.regime_policy),
        "regime_execution_policy": case.regime_execution_policy.canonical_payload(),
        "rolling_window_policy": _case_window_policy_payload(case),
    }


def _validate_policy_context(bundle: ReplayBundle) -> tuple[str, float]:
    collapsed = bundle.collapsed_cases()
    reference = _policy_context_payload(collapsed[0])
    for case in collapsed[1:]:
        if _policy_context_payload(case) != reference:
            raise ValueError("untuned policy context drifted across holdout corpus")
    return _sha256(reference), reference["engine_policy"]["observe_net_edge"] * 10_000.0


def _candidate_results(bundle: ReplayBundle, candidate: PolicyCandidate) -> tuple[ReplayResult, ...]:
    results: list[ReplayResult] = []
    for case in bundle.collapsed_cases():
        engine_policy = replace(
            case.engine_policy,
            execute_net_edge=candidate.execute_net_edge_bps / 10_000.0,
        )
        results.append(replay_case(case, engine_policy=engine_policy))
    return tuple(results)


def evaluate_policy_candidate(
    bundle: ReplayBundle,
    candidate: PolicyCandidate,
    policy: HoldoutPolicy,
    *,
    min_truth_events: int,
) -> PolicyEvaluation:
    results = _candidate_results(bundle, candidate)
    metrics = calculate_replay_metrics(results)
    execute_sim_count = sum(result.expected_verdict is Verdict.EXECUTE_SIM for result in results)
    truth_events = metrics.true_positive + metrics.false_positive
    survival_events = truth_events + metrics.expired
    truth_lb = wilson_lower_bound(
        metrics.true_positive,
        truth_events,
        z=policy.confidence_z,
    )
    survival_lb = wilson_lower_bound(
        truth_events,
        survival_events,
        z=policy.confidence_z,
    )
    mean_error = metrics.mean_prediction_error_bps
    overprediction_penalty = max(0.0, -(mean_error if mean_error is not None else 0.0))
    reasons: list[str] = []
    if truth_events < min_truth_events:
        reasons.append("INSUFFICIENT_TRUTH_EVENTS")
    if truth_lb is None or truth_lb < policy.min_truth_rate_lower_bound:
        reasons.append("TRUTH_LOWER_BOUND_BELOW_FLOOR")
    if survival_lb is None or survival_lb < policy.min_survival_rate_lower_bound:
        reasons.append("SURVIVAL_LOWER_BOUND_BELOW_FLOOR")
    return PolicyEvaluation(
        candidate=candidate,
        metrics=metrics,
        execute_sim_count=execute_sim_count,
        truth_events=truth_events,
        survival_events=survival_events,
        truth_rate_lower_bound=truth_lb,
        survival_rate_lower_bound=survival_lb,
        overprediction_penalty_bps=overprediction_penalty,
        results_sha256=_sha256([result.to_payload() for result in results]),
        eligible=not reasons,
        reasons=tuple(reasons),
    )


def _selection_key(evaluation: PolicyEvaluation) -> tuple[Any, ...]:
    if evaluation.truth_rate_lower_bound is None or evaluation.survival_rate_lower_bound is None:
        raise ValueError("eligible calibration evaluation is missing lower bounds")
    return (
        -evaluation.truth_rate_lower_bound,
        -evaluation.survival_rate_lower_bound,
        -evaluation.truth_events,
        evaluation.metrics.indeterminate,
        evaluation.overprediction_penalty_bps,
        -evaluation.candidate.execute_net_edge_bps,
    )


@dataclass(frozen=True, slots=True)
class HoldoutReport:
    source_bundle_sha256: str
    policy_context_sha256: str
    holdout_policy: HoldoutPolicy
    candidate_grid: CandidateGrid
    status: HoldoutStatus
    split: HoldoutSplitSummary | None
    calibration_evaluations: tuple[PolicyEvaluation, ...]
    selected_candidate: PolicyCandidate | None
    validation_evaluation: PolicyEvaluation | None
    reasons: tuple[str, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "calibration_evaluations", tuple(self.calibration_evaluations))
        object.__setattr__(self, "reasons", tuple(self.reasons))
        if self.status is HoldoutStatus.PASSED_HOLDOUT:
            if self.selected_candidate is None or self.validation_evaluation is None:
                raise ValueError("passed holdout requires selected candidate and validation")
            if not self.validation_evaluation.eligible:
                raise ValueError("passed holdout cannot contain failed validation")

    def canonical_payload(self) -> dict[str, Any]:
        return {
            "schema": _HOLDOUT_REPORT_SCHEMA,
            "source_bundle_sha256": self.source_bundle_sha256,
            "policy_context_sha256": self.policy_context_sha256,
            "holdout_policy": asdict(self.holdout_policy),
            "candidate_grid": self.candidate_grid.to_payload(),
            "status": self.status.value,
            "split": self.split.to_payload() if self.split is not None else None,
            "calibration_evaluations": [
                evaluation.to_payload() for evaluation in self.calibration_evaluations
            ],
            "selected_candidate": (
                self.selected_candidate.to_payload()
                if self.selected_candidate is not None
                else None
            ),
            "validation_evaluation": (
                self.validation_evaluation.to_payload()
                if self.validation_evaluation is not None
                else None
            ),
            "reasons": list(self.reasons),
            "selection_rule": _SELECTION_RULE,
            "validation_not_used_for_selection": True,
            "advisory_only": True,
        }

    @property
    def sha256(self) -> str:
        return _sha256(self.canonical_payload())

    def to_envelope(self) -> dict[str, Any]:
        return {"payload": self.canonical_payload(), "sha256": self.sha256}


def verify_holdout_report_envelope(envelope: Mapping[str, Any]) -> dict[str, Any]:
    try:
        payload = envelope["payload"]
        supplied_sha = envelope["sha256"]
    except KeyError as exc:
        raise ValueError("holdout report envelope is incomplete") from exc
    if not isinstance(payload, dict) or not isinstance(supplied_sha, str):
        raise ValueError("holdout report envelope has invalid types")
    if payload.get("schema") != _HOLDOUT_REPORT_SCHEMA:
        raise ValueError("unsupported holdout report schema")
    expected_keys = {
        "schema",
        "source_bundle_sha256",
        "policy_context_sha256",
        "holdout_policy",
        "candidate_grid",
        "status",
        "split",
        "calibration_evaluations",
        "selected_candidate",
        "validation_evaluation",
        "reasons",
        "selection_rule",
        "validation_not_used_for_selection",
        "advisory_only",
    }
    if set(payload) != expected_keys:
        raise ValueError("holdout report payload fields are not canonical")
    if payload["selection_rule"] != _SELECTION_RULE:
        raise ValueError("holdout report selection rule is invalid")
    if payload["validation_not_used_for_selection"] is not True:
        raise ValueError("holdout report validation-selection firewall is invalid")
    if payload["advisory_only"] is not True:
        raise ValueError("holdout report must remain advisory-only")
    if payload["status"] not in {status.value for status in HoldoutStatus}:
        raise ValueError("holdout report status is invalid")
    digest = _sha256(payload)
    if not hmac.compare_digest(digest, supplied_sha):
        raise ValueError("holdout report SHA-256 does not match payload")
    _canonical_json(payload)
    return dict(payload)


def run_holdout_calibration(
    bundle: ReplayBundle,
    grid: CandidateGrid,
    policy: HoldoutPolicy,
) -> HoldoutReport:
    policy_context_sha256, observe_net_edge_bps = _validate_policy_context(bundle)
    candidates = grid.candidates()
    for candidate in candidates:
        if candidate.execute_net_edge_bps <= observe_net_edge_bps:
            raise ValueError(
                "candidate execute threshold must exceed the corpus observe threshold"
            )

    try:
        split = split_replay_bundle(bundle, policy)
    except HoldoutSplitError as exc:
        return HoldoutReport(
            source_bundle_sha256=bundle.sha256,
            policy_context_sha256=policy_context_sha256,
            holdout_policy=policy,
            candidate_grid=grid,
            status=HoldoutStatus.INSUFFICIENT_CORPUS,
            split=None,
            calibration_evaluations=(),
            selected_candidate=None,
            validation_evaluation=None,
            reasons=(str(exc),),
        )

    calibration_evaluations = tuple(
        evaluate_policy_candidate(
            split.calibration,
            candidate,
            policy,
            min_truth_events=policy.min_calibration_truth_events,
        )
        for candidate in candidates
    )
    eligible = [evaluation for evaluation in calibration_evaluations if evaluation.eligible]
    if not eligible:
        insufficient = all(
            evaluation.truth_events < policy.min_calibration_truth_events
            for evaluation in calibration_evaluations
        )
        status = (
            HoldoutStatus.INSUFFICIENT_CALIBRATION
            if insufficient
            else HoldoutStatus.NO_ELIGIBLE_CALIBRATION_POLICY
        )
        return HoldoutReport(
            source_bundle_sha256=bundle.sha256,
            policy_context_sha256=policy_context_sha256,
            holdout_policy=policy,
            candidate_grid=grid,
            status=status,
            split=split.summary,
            calibration_evaluations=calibration_evaluations,
            selected_candidate=None,
            validation_evaluation=None,
            reasons=("no calibration candidate met the explicit guardrails",),
        )

    selected_evaluation = sorted(eligible, key=_selection_key)[0]
    selected_candidate = selected_evaluation.candidate

    validation_evaluation = evaluate_policy_candidate(
        split.validation,
        selected_candidate,
        policy,
        min_truth_events=policy.min_validation_truth_events,
    )
    if validation_evaluation.truth_events < policy.min_validation_truth_events:
        status = HoldoutStatus.INSUFFICIENT_VALIDATION
        reasons = ("selected calibration policy lacks validation truth support",)
    elif not validation_evaluation.eligible:
        status = HoldoutStatus.VALIDATION_FAILED
        reasons = ("selected calibration policy failed out-of-sample guardrails",)
    else:
        status = HoldoutStatus.PASSED_HOLDOUT
        reasons = ("selected calibration policy passed untouched validation guardrails",)

    return HoldoutReport(
        source_bundle_sha256=bundle.sha256,
        policy_context_sha256=policy_context_sha256,
        holdout_policy=policy,
        candidate_grid=grid,
        status=status,
        split=split.summary,
        calibration_evaluations=calibration_evaluations,
        selected_candidate=selected_candidate,
        validation_evaluation=validation_evaluation,
        reasons=reasons,
    )
