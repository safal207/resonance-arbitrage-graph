from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass, replace
from enum import Enum
import hashlib
import hmac
import json
import math
from typing import Any

from .holdout import HoldoutPolicy, HoldoutSplitError, split_replay_bundle, wilson_lower_bound
from .model import Verdict
from .regime import RegimePolicy
from .regime_gate import RegimeAction
from .replay import ReplayBundle, ReplayMetrics, ReplayResult, calculate_replay_metrics, replay_case


_JOINT_REPORT_SCHEMA = "resonance.arbitrage.joint-holdout-report/v0.1"
_SELECTION_RULE = (
    "calibration_only:truth_lower_bound>survival_lower_bound>truth_events>"
    "lower_indeterminate>overprediction_penalty>higher_execute_threshold>"
    "lower_volatility_threshold"
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


class JointHoldoutStatus(str, Enum):
    PASSED_HOLDOUT = "PASSED_HOLDOUT"
    INSUFFICIENT_CORPUS = "INSUFFICIENT_CORPUS"
    INSUFFICIENT_CALIBRATION = "INSUFFICIENT_CALIBRATION"
    NO_ELIGIBLE_CALIBRATION_POLICY = "NO_ELIGIBLE_CALIBRATION_POLICY"
    INSUFFICIENT_VALIDATION = "INSUFFICIENT_VALIDATION"
    INSUFFICIENT_VALIDATION_CAUSAL_SUPPORT = "INSUFFICIENT_VALIDATION_CAUSAL_SUPPORT"
    VALIDATION_FAILED = "VALIDATION_FAILED"


@dataclass(frozen=True, slots=True)
class JointHoldoutPolicy:
    holdout: HoldoutPolicy
    min_calibration_execute_causal_changes: int = 1
    min_calibration_volatility_causal_changes: int = 1
    min_validation_execute_causal_changes: int = 1
    min_validation_volatility_causal_changes: int = 1

    def __post_init__(self) -> None:
        if not isinstance(self.holdout, HoldoutPolicy):
            raise ValueError("holdout must be HoldoutPolicy")
        for name in (
            "min_calibration_execute_causal_changes",
            "min_calibration_volatility_causal_changes",
            "min_validation_execute_causal_changes",
            "min_validation_volatility_causal_changes",
        ):
            if getattr(self, name) < 0:
                raise ValueError(f"{name} must be non-negative")

    def to_payload(self) -> dict[str, Any]:
        return {
            "holdout": asdict(self.holdout),
            "min_calibration_execute_causal_changes": self.min_calibration_execute_causal_changes,
            "min_calibration_volatility_causal_changes": self.min_calibration_volatility_causal_changes,
            "min_validation_execute_causal_changes": self.min_validation_execute_causal_changes,
            "min_validation_volatility_causal_changes": self.min_validation_volatility_causal_changes,
        }


@dataclass(frozen=True, slots=True)
class JointPolicyCandidate:
    execute_net_edge_bps: float
    volatile_return_bps: float

    def __post_init__(self) -> None:
        if not math.isfinite(self.execute_net_edge_bps) or self.execute_net_edge_bps <= 0:
            raise ValueError("execute_net_edge_bps must be finite and positive")
        if not math.isfinite(self.volatile_return_bps) or self.volatile_return_bps < 0:
            raise ValueError("volatile_return_bps must be finite and non-negative")

    def to_payload(self) -> dict[str, float]:
        return {
            "execute_net_edge_bps": self.execute_net_edge_bps,
            "volatile_return_bps": self.volatile_return_bps,
        }


@dataclass(frozen=True, slots=True)
class JointCandidateGrid:
    execute_net_edge_bps: tuple[float, ...]
    volatile_return_bps: tuple[float, ...]

    def __post_init__(self) -> None:
        execute = tuple(sorted(set(self.execute_net_edge_bps)))
        volatile = tuple(sorted(set(self.volatile_return_bps)))
        object.__setattr__(self, "execute_net_edge_bps", execute)
        object.__setattr__(self, "volatile_return_bps", volatile)
        if not execute or not volatile:
            raise ValueError("joint candidate grid dimensions must be non-empty")
        for value in execute:
            if not math.isfinite(value) or value <= 0:
                raise ValueError("execute threshold grid values must be finite and positive")
        for value in volatile:
            if not math.isfinite(value) or value < 0:
                raise ValueError("volatility threshold grid values must be finite and non-negative")

    def candidates(self) -> tuple[JointPolicyCandidate, ...]:
        return tuple(
            JointPolicyCandidate(execute_net_edge_bps=execute, volatile_return_bps=volatile)
            for execute in self.execute_net_edge_bps
            for volatile in self.volatile_return_bps
        )

    def to_payload(self) -> dict[str, list[float]]:
        return {
            "execute_net_edge_bps": list(self.execute_net_edge_bps),
            "volatile_return_bps": list(self.volatile_return_bps),
        }


@dataclass(frozen=True, slots=True)
class CausalSupport:
    execute_final_verdict_changes: int
    volatility_regime_label_changes: int
    volatility_final_verdict_changes: int
    joint_final_verdict_changes: int
    execute_operation_ids: tuple[str, ...]
    volatility_operation_ids: tuple[str, ...]
    joint_operation_ids: tuple[str, ...]

    def to_payload(self) -> dict[str, Any]:
        return {
            "execute_final_verdict_changes": self.execute_final_verdict_changes,
            "volatility_regime_label_changes": self.volatility_regime_label_changes,
            "volatility_final_verdict_changes": self.volatility_final_verdict_changes,
            "joint_final_verdict_changes": self.joint_final_verdict_changes,
            "execute_operation_ids": list(self.execute_operation_ids),
            "volatility_operation_ids": list(self.volatility_operation_ids),
            "joint_operation_ids": list(self.joint_operation_ids),
        }


@dataclass(frozen=True, slots=True)
class JointPolicyEvaluation:
    candidate: JointPolicyCandidate
    metrics: ReplayMetrics
    execute_sim_count: int
    truth_events: int
    survival_events: int
    truth_rate_lower_bound: float | None
    survival_rate_lower_bound: float | None
    overprediction_penalty_bps: float
    causal_support: CausalSupport
    results_sha256: str
    baseline_results_sha256: str
    execute_only_results_sha256: str
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
            "causal_support": self.causal_support.to_payload(),
            "results_sha256": self.results_sha256,
            "baseline_results_sha256": self.baseline_results_sha256,
            "execute_only_results_sha256": self.execute_only_results_sha256,
            "eligible": self.eligible,
            "reasons": list(self.reasons),
        }


@dataclass(frozen=True, slots=True)
class JointPolicyContext:
    sha256: str
    baseline_execute_net_edge_bps: float
    baseline_volatile_return_bps: float
    observe_net_edge_bps: float
    frozen_context: dict[str, Any]

    def to_payload(self) -> dict[str, Any]:
        return {
            "sha256": self.sha256,
            "baseline_execute_net_edge_bps": self.baseline_execute_net_edge_bps,
            "baseline_volatile_return_bps": self.baseline_volatile_return_bps,
            "observe_net_edge_bps": self.observe_net_edge_bps,
            "frozen_context": self.frozen_context,
        }


def _window_policy_payload(case: Any) -> dict[str, Any]:
    policies = {
        _canonical_json(asdict(window.policy)): asdict(window.policy)
        for window in case.windows_by_market.values()
    }
    if not policies:
        raise ValueError("joint holdout case has no rolling-window policy context")
    if len(policies) != 1:
        raise ValueError("rolling-window policy drifted within replay case")
    return next(iter(policies.values()))


def _frozen_context_payload(case: Any) -> dict[str, Any]:
    engine = asdict(case.engine_policy)
    engine.pop("execute_net_edge")
    regime = asdict(case.regime_policy)
    regime.pop("volatile_return_bps")
    return {
        "engine_policy": engine,
        "regime_policy": regime,
        "regime_execution_policy": case.regime_execution_policy.canonical_payload(),
        "rolling_window_policy": _window_policy_payload(case),
    }


def validate_joint_policy_context(bundle: ReplayBundle) -> JointPolicyContext:
    collapsed = bundle.collapsed_cases()
    reference = _frozen_context_payload(collapsed[0])
    baseline_execute = collapsed[0].engine_policy.execute_net_edge * 10_000.0
    baseline_volatile = collapsed[0].regime_policy.volatile_return_bps

    gate = collapsed[0].regime_execution_policy
    if gate.normal is not RegimeAction.ALLOW or gate.volatile not in {
        RegimeAction.OBSERVE_ONLY,
        RegimeAction.REJECT,
    }:
        raise ValueError(
            "joint volatility calibration requires NORMAL=ALLOW and VOLATILE to be suppressive"
        )

    for case in collapsed[1:]:
        if _frozen_context_payload(case) != reference:
            raise ValueError("untuned policy context drifted across joint holdout corpus")
        if not math.isclose(
            case.engine_policy.execute_net_edge * 10_000.0,
            baseline_execute,
            rel_tol=0.0,
            abs_tol=1e-12,
        ):
            raise ValueError("baseline execute threshold drifted across joint holdout corpus")
        if not math.isclose(
            case.regime_policy.volatile_return_bps,
            baseline_volatile,
            rel_tol=0.0,
            abs_tol=1e-12,
        ):
            raise ValueError("baseline volatility threshold drifted across joint holdout corpus")

    return JointPolicyContext(
        sha256=_sha256(reference),
        baseline_execute_net_edge_bps=baseline_execute,
        baseline_volatile_return_bps=baseline_volatile,
        observe_net_edge_bps=reference["engine_policy"]["observe_net_edge"] * 10_000.0,
        frozen_context=reference,
    )


def _run_results(
    bundle: ReplayBundle,
    *,
    execute_net_edge_bps: float,
    volatile_return_bps: float,
) -> tuple[ReplayResult, ...]:
    results: list[ReplayResult] = []
    for case in bundle.collapsed_cases():
        engine_policy = replace(
            case.engine_policy,
            execute_net_edge=execute_net_edge_bps / 10_000.0,
        )
        regime_policy = replace(
            case.regime_policy,
            volatile_return_bps=volatile_return_bps,
        )
        results.append(
            replay_case(
                case,
                engine_policy=engine_policy,
                regime_policy=regime_policy,
            )
        )
    return tuple(results)


def _result_map(results: Sequence[ReplayResult]) -> dict[str, ReplayResult]:
    mapping = {result.logical_operation_id: result for result in results}
    if len(mapping) != len(results):
        raise ValueError("joint holdout results contain duplicate logical operations")
    return mapping


def _causal_support(
    baseline_results: Sequence[ReplayResult],
    execute_only_results: Sequence[ReplayResult],
    candidate_results: Sequence[ReplayResult],
) -> CausalSupport:
    baseline = _result_map(baseline_results)
    execute_only = _result_map(execute_only_results)
    candidate = _result_map(candidate_results)
    if set(baseline) != set(execute_only) or set(baseline) != set(candidate):
        raise ValueError("causal support result populations do not match")

    execute_ids: list[str] = []
    volatility_ids: list[str] = []
    joint_ids: list[str] = []
    label_changes = 0
    for operation_id in sorted(baseline):
        base = baseline[operation_id]
        execute = execute_only[operation_id]
        final = candidate[operation_id]
        if execute.expected_verdict is not base.expected_verdict:
            execute_ids.append(operation_id)
        if final.regime is not execute.regime:
            label_changes += 1
        if final.expected_verdict is not execute.expected_verdict:
            volatility_ids.append(operation_id)
        if final.expected_verdict is not base.expected_verdict:
            joint_ids.append(operation_id)

    return CausalSupport(
        execute_final_verdict_changes=len(execute_ids),
        volatility_regime_label_changes=label_changes,
        volatility_final_verdict_changes=len(volatility_ids),
        joint_final_verdict_changes=len(joint_ids),
        execute_operation_ids=tuple(execute_ids),
        volatility_operation_ids=tuple(volatility_ids),
        joint_operation_ids=tuple(joint_ids),
    )


def evaluate_joint_policy_candidate(
    bundle: ReplayBundle,
    candidate: JointPolicyCandidate,
    policy: JointHoldoutPolicy,
    context: JointPolicyContext,
    *,
    min_truth_events: int,
    min_execute_causal_changes: int,
    min_volatility_causal_changes: int,
) -> JointPolicyEvaluation:
    baseline_results = _run_results(
        bundle,
        execute_net_edge_bps=context.baseline_execute_net_edge_bps,
        volatile_return_bps=context.baseline_volatile_return_bps,
    )
    execute_only_results = _run_results(
        bundle,
        execute_net_edge_bps=candidate.execute_net_edge_bps,
        volatile_return_bps=context.baseline_volatile_return_bps,
    )
    results = _run_results(
        bundle,
        execute_net_edge_bps=candidate.execute_net_edge_bps,
        volatile_return_bps=candidate.volatile_return_bps,
    )
    metrics = calculate_replay_metrics(results)
    support = _causal_support(baseline_results, execute_only_results, results)
    execute_sim_count = sum(result.expected_verdict is Verdict.EXECUTE_SIM for result in results)
    truth_events = metrics.true_positive + metrics.false_positive
    survival_events = truth_events + metrics.expired
    truth_lb = wilson_lower_bound(
        metrics.true_positive,
        truth_events,
        z=policy.holdout.confidence_z,
    )
    survival_lb = wilson_lower_bound(
        truth_events,
        survival_events,
        z=policy.holdout.confidence_z,
    )
    mean_error = metrics.mean_prediction_error_bps
    overprediction_penalty = max(0.0, -(mean_error if mean_error is not None else 0.0))

    reasons: list[str] = []
    if truth_events < min_truth_events:
        reasons.append("INSUFFICIENT_TRUTH_EVENTS")
    if truth_lb is None or truth_lb < policy.holdout.min_truth_rate_lower_bound:
        reasons.append("TRUTH_LOWER_BOUND_BELOW_FLOOR")
    if survival_lb is None or survival_lb < policy.holdout.min_survival_rate_lower_bound:
        reasons.append("SURVIVAL_LOWER_BOUND_BELOW_FLOOR")
    if support.execute_final_verdict_changes < min_execute_causal_changes:
        reasons.append("INSUFFICIENT_EXECUTE_CAUSAL_SUPPORT")
    if support.volatility_final_verdict_changes < min_volatility_causal_changes:
        reasons.append("INSUFFICIENT_VOLATILITY_CAUSAL_SUPPORT")

    return JointPolicyEvaluation(
        candidate=candidate,
        metrics=metrics,
        execute_sim_count=execute_sim_count,
        truth_events=truth_events,
        survival_events=survival_events,
        truth_rate_lower_bound=truth_lb,
        survival_rate_lower_bound=survival_lb,
        overprediction_penalty_bps=overprediction_penalty,
        causal_support=support,
        results_sha256=_sha256([result.to_payload() for result in results]),
        baseline_results_sha256=_sha256([result.to_payload() for result in baseline_results]),
        execute_only_results_sha256=_sha256([result.to_payload() for result in execute_only_results]),
        eligible=not reasons,
        reasons=tuple(reasons),
    )


def _selection_key(evaluation: JointPolicyEvaluation) -> tuple[Any, ...]:
    if evaluation.truth_rate_lower_bound is None or evaluation.survival_rate_lower_bound is None:
        raise ValueError("eligible joint calibration evaluation is missing lower bounds")
    return (
        -evaluation.truth_rate_lower_bound,
        -evaluation.survival_rate_lower_bound,
        -evaluation.truth_events,
        evaluation.metrics.indeterminate,
        evaluation.overprediction_penalty_bps,
        -evaluation.candidate.execute_net_edge_bps,
        evaluation.candidate.volatile_return_bps,
    )


@dataclass(frozen=True, slots=True)
class JointHoldoutReport:
    source_bundle_sha256: str
    policy_context: JointPolicyContext
    joint_policy: JointHoldoutPolicy
    candidate_grid: JointCandidateGrid
    status: JointHoldoutStatus
    split: dict[str, Any] | None
    calibration_evaluations: tuple[JointPolicyEvaluation, ...]
    selected_candidate: JointPolicyCandidate | None
    validation_evaluation: JointPolicyEvaluation | None
    reasons: tuple[str, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "calibration_evaluations", tuple(self.calibration_evaluations))
        object.__setattr__(self, "reasons", tuple(self.reasons))
        if self.status is JointHoldoutStatus.PASSED_HOLDOUT:
            if self.selected_candidate is None or self.validation_evaluation is None:
                raise ValueError("passed joint holdout requires selected candidate and validation")
            if not self.validation_evaluation.eligible:
                raise ValueError("passed joint holdout cannot contain failed validation")

    def canonical_payload(self) -> dict[str, Any]:
        return {
            "schema": _JOINT_REPORT_SCHEMA,
            "source_bundle_sha256": self.source_bundle_sha256,
            "policy_context": self.policy_context.to_payload(),
            "joint_policy": self.joint_policy.to_payload(),
            "candidate_grid": self.candidate_grid.to_payload(),
            "status": self.status.value,
            "split": self.split,
            "calibration_evaluations": [item.to_payload() for item in self.calibration_evaluations],
            "selected_candidate": self.selected_candidate.to_payload() if self.selected_candidate else None,
            "validation_evaluation": self.validation_evaluation.to_payload() if self.validation_evaluation else None,
            "reasons": list(self.reasons),
            "selection_rule": _SELECTION_RULE,
            "causal_support_is_eligibility_not_objective": True,
            "validation_not_used_for_selection": True,
            "advisory_only": True,
        }

    @property
    def sha256(self) -> str:
        return _sha256(self.canonical_payload())

    def to_envelope(self) -> dict[str, Any]:
        return {"payload": self.canonical_payload(), "sha256": self.sha256}


def verify_joint_holdout_report_envelope(envelope: Mapping[str, Any]) -> dict[str, Any]:
    try:
        payload = envelope["payload"]
        supplied_sha = envelope["sha256"]
    except KeyError as exc:
        raise ValueError("joint holdout report envelope is incomplete") from exc
    if not isinstance(payload, dict) or not isinstance(supplied_sha, str):
        raise ValueError("joint holdout report envelope has invalid types")
    if payload.get("schema") != _JOINT_REPORT_SCHEMA:
        raise ValueError("unsupported joint holdout report schema")
    if payload.get("selection_rule") != _SELECTION_RULE:
        raise ValueError("joint holdout selection rule is invalid")
    if payload.get("causal_support_is_eligibility_not_objective") is not True:
        raise ValueError("joint holdout causal-support semantics are invalid")
    if payload.get("validation_not_used_for_selection") is not True:
        raise ValueError("joint holdout validation-selection firewall is invalid")
    if payload.get("advisory_only") is not True:
        raise ValueError("joint holdout report must remain advisory-only")
    if payload.get("status") not in {status.value for status in JointHoldoutStatus}:
        raise ValueError("joint holdout report status is invalid")
    digest = _sha256(payload)
    if not hmac.compare_digest(digest, supplied_sha):
        raise ValueError("joint holdout report SHA-256 does not match payload")
    _canonical_json(payload)
    return dict(payload)


def run_joint_holdout_calibration(
    bundle: ReplayBundle,
    grid: JointCandidateGrid,
    policy: JointHoldoutPolicy,
) -> JointHoldoutReport:
    context = validate_joint_policy_context(bundle)
    candidates = grid.candidates()
    for candidate in candidates:
        if candidate.execute_net_edge_bps <= context.observe_net_edge_bps:
            raise ValueError("candidate execute threshold must exceed corpus observe threshold")

    try:
        split = split_replay_bundle(bundle, policy.holdout)
    except HoldoutSplitError as exc:
        return JointHoldoutReport(
            source_bundle_sha256=bundle.sha256,
            policy_context=context,
            joint_policy=policy,
            candidate_grid=grid,
            status=JointHoldoutStatus.INSUFFICIENT_CORPUS,
            split=None,
            calibration_evaluations=(),
            selected_candidate=None,
            validation_evaluation=None,
            reasons=(str(exc),),
        )

    calibration_evaluations = tuple(
        evaluate_joint_policy_candidate(
            split.calibration,
            candidate,
            policy,
            context,
            min_truth_events=policy.holdout.min_calibration_truth_events,
            min_execute_causal_changes=policy.min_calibration_execute_causal_changes,
            min_volatility_causal_changes=policy.min_calibration_volatility_causal_changes,
        )
        for candidate in candidates
    )
    eligible = [item for item in calibration_evaluations if item.eligible]
    split_payload = split.summary.to_payload()
    if not eligible:
        insufficient_truth = all(
            item.truth_events < policy.holdout.min_calibration_truth_events
            for item in calibration_evaluations
        )
        status = (
            JointHoldoutStatus.INSUFFICIENT_CALIBRATION
            if insufficient_truth
            else JointHoldoutStatus.NO_ELIGIBLE_CALIBRATION_POLICY
        )
        return JointHoldoutReport(
            source_bundle_sha256=bundle.sha256,
            policy_context=context,
            joint_policy=policy,
            candidate_grid=grid,
            status=status,
            split=split_payload,
            calibration_evaluations=calibration_evaluations,
            selected_candidate=None,
            validation_evaluation=None,
            reasons=("no joint calibration candidate met evidence and causal-support guardrails",),
        )

    selected = sorted(eligible, key=_selection_key)[0].candidate
    validation = evaluate_joint_policy_candidate(
        split.validation,
        selected,
        policy,
        context,
        min_truth_events=policy.holdout.min_validation_truth_events,
        min_execute_causal_changes=policy.min_validation_execute_causal_changes,
        min_volatility_causal_changes=policy.min_validation_volatility_causal_changes,
    )

    if validation.truth_events < policy.holdout.min_validation_truth_events:
        status = JointHoldoutStatus.INSUFFICIENT_VALIDATION
        reasons = ("selected joint policy lacks validation truth support",)
    elif (
        validation.causal_support.execute_final_verdict_changes
        < policy.min_validation_execute_causal_changes
        or validation.causal_support.volatility_final_verdict_changes
        < policy.min_validation_volatility_causal_changes
    ):
        status = JointHoldoutStatus.INSUFFICIENT_VALIDATION_CAUSAL_SUPPORT
        reasons = ("selected joint policy lacks out-of-sample causal support",)
    elif not validation.eligible:
        status = JointHoldoutStatus.VALIDATION_FAILED
        reasons = ("selected joint policy failed untouched validation guardrails",)
    else:
        status = JointHoldoutStatus.PASSED_HOLDOUT
        reasons = ("selected joint policy passed untouched validation and causal-support guardrails",)

    return JointHoldoutReport(
        source_bundle_sha256=bundle.sha256,
        policy_context=context,
        joint_policy=policy,
        candidate_grid=grid,
        status=status,
        split=split_payload,
        calibration_evaluations=calibration_evaluations,
        selected_candidate=selected,
        validation_evaluation=validation,
        reasons=reasons,
    )
