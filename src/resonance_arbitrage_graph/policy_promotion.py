from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from enum import Enum
import hashlib
import hmac
import json
import math
from typing import Any

from .joint_holdout import JointPolicyCandidate
from .replay import ReplayBundle
from .stability_decomposition import (
    DecompositionStatus,
    StabilityDecompositionReport,
    verify_stability_decomposition_bundle_binding,
)
from .walk_forward import WalkForwardReport, WalkForwardStatus


_PROMOTION_SCHEMA = "resonance.arbitrage.policy-promotion-report/v0.1"


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


def _validate_sha256(value: str, name: str) -> None:
    if not isinstance(value, str) or len(value) != 64:
        raise ValueError(f"{name} must be a 64-character SHA-256 hex digest")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{name} must be hexadecimal") from exc


def _candidate_key(candidate: JointPolicyCandidate) -> tuple[float, float]:
    return (candidate.execute_net_edge_bps, candidate.volatile_return_bps)


class PolicyPromotionStatus(str, Enum):
    PROMOTED = "PROMOTED"
    BLOCKED_WALK_FORWARD = "BLOCKED_WALK_FORWARD"
    BLOCKED_DECOMPOSITION = "BLOCKED_DECOMPOSITION"
    INSUFFICIENT_SELECTED_POLICIES = "INSUFFICIENT_SELECTED_POLICIES"
    AMBIGUOUS_CALIBRATION_CONSENSUS = "AMBIGUOUS_CALIBRATION_CONSENSUS"
    CONSENSUS_BELOW_FLOOR = "CONSENSUS_BELOW_FLOOR"
    INSUFFICIENT_CANDIDATE_SUPPORT = "INSUFFICIENT_CANDIDATE_SUPPORT"
    CANDIDATE_VALIDATION_BELOW_FLOOR = "CANDIDATE_VALIDATION_BELOW_FLOOR"


@dataclass(frozen=True, slots=True)
class PolicyPromotionGuardrails:
    min_selected_policy_folds: int = 3
    min_candidate_supporting_folds: int = 2
    min_consensus_fraction: float = 2.0 / 3.0
    min_candidate_validation_pass_rate: float = 2.0 / 3.0

    def __post_init__(self) -> None:
        if self.min_selected_policy_folds < 1:
            raise ValueError("min_selected_policy_folds must be >= 1")
        if self.min_candidate_supporting_folds < 1:
            raise ValueError("min_candidate_supporting_folds must be >= 1")
        for name in ("min_consensus_fraction", "min_candidate_validation_pass_rate"):
            value = getattr(self, name)
            if not math.isfinite(value) or not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be finite and in [0, 1]")

    def to_payload(self) -> dict[str, Any]:
        return {
            "min_selected_policy_folds": self.min_selected_policy_folds,
            "min_candidate_supporting_folds": self.min_candidate_supporting_folds,
            "min_consensus_fraction": self.min_consensus_fraction,
            "min_candidate_validation_pass_rate": self.min_candidate_validation_pass_rate,
        }


@dataclass(frozen=True, slots=True)
class CalibrationCandidateSupport:
    candidate: JointPolicyCandidate
    fold_indexes: tuple[int, ...]
    validation_passed_fold_indexes: tuple[int, ...]
    validation_failed_fold_indexes: tuple[int, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "fold_indexes", tuple(self.fold_indexes))
        object.__setattr__(
            self,
            "validation_passed_fold_indexes",
            tuple(self.validation_passed_fold_indexes),
        )
        object.__setattr__(
            self,
            "validation_failed_fold_indexes",
            tuple(self.validation_failed_fold_indexes),
        )
        if not isinstance(self.candidate, JointPolicyCandidate):
            raise ValueError("candidate support requires JointPolicyCandidate")
        if not self.fold_indexes:
            raise ValueError("candidate support requires at least one fold")
        for name in (
            "fold_indexes",
            "validation_passed_fold_indexes",
            "validation_failed_fold_indexes",
        ):
            values = getattr(self, name)
            if tuple(sorted(values)) != values or len(set(values)) != len(values):
                raise ValueError(f"{name} must be sorted and unique")
            if any(value < 1 for value in values):
                raise ValueError(f"{name} must contain positive fold indexes")
        passed = set(self.validation_passed_fold_indexes)
        failed = set(self.validation_failed_fold_indexes)
        if passed & failed:
            raise ValueError("validation passed/failed fold sets overlap")
        if passed | failed != set(self.fold_indexes):
            raise ValueError("validation fold partition must equal candidate support folds")

    @property
    def support_count(self) -> int:
        return len(self.fold_indexes)

    @property
    def validation_pass_rate(self) -> float:
        return len(self.validation_passed_fold_indexes) / len(self.fold_indexes)

    def to_payload(self) -> dict[str, Any]:
        return {
            "candidate": self.candidate.to_payload(),
            "fold_indexes": list(self.fold_indexes),
            "validation_passed_fold_indexes": list(
                self.validation_passed_fold_indexes
            ),
            "validation_failed_fold_indexes": list(
                self.validation_failed_fold_indexes
            ),
            "support_count": self.support_count,
            "validation_pass_rate": self.validation_pass_rate,
        }


@dataclass(frozen=True, slots=True)
class PolicyPromotionDecision:
    status: PolicyPromotionStatus
    candidate: JointPolicyCandidate | None
    selected_policy_folds: int
    supporting_fold_indexes: tuple[int, ...]
    validation_passed_fold_indexes: tuple[int, ...]
    validation_failed_fold_indexes: tuple[int, ...]
    consensus_fraction: float | None
    candidate_validation_pass_rate: float | None
    reasons: tuple[str, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "supporting_fold_indexes", tuple(self.supporting_fold_indexes))
        object.__setattr__(
            self,
            "validation_passed_fold_indexes",
            tuple(self.validation_passed_fold_indexes),
        )
        object.__setattr__(
            self,
            "validation_failed_fold_indexes",
            tuple(self.validation_failed_fold_indexes),
        )
        object.__setattr__(self, "reasons", tuple(self.reasons))
        if self.selected_policy_folds < 0:
            raise ValueError("selected_policy_folds must be non-negative")
        if self.status is PolicyPromotionStatus.PROMOTED and self.candidate is None:
            raise ValueError("promoted decision requires a candidate")
        if self.candidate is None:
            if self.supporting_fold_indexes:
                raise ValueError("candidate-less decision cannot claim supporting folds")
            if self.consensus_fraction is not None:
                raise ValueError("candidate-less decision cannot claim consensus fraction")
            if self.candidate_validation_pass_rate is not None:
                raise ValueError("candidate-less decision cannot claim validation pass rate")

    def to_payload(self) -> dict[str, Any]:
        return {
            "status": self.status.value,
            "candidate": self.candidate.to_payload() if self.candidate else None,
            "selected_policy_folds": self.selected_policy_folds,
            "supporting_fold_indexes": list(self.supporting_fold_indexes),
            "validation_passed_fold_indexes": list(
                self.validation_passed_fold_indexes
            ),
            "validation_failed_fold_indexes": list(
                self.validation_failed_fold_indexes
            ),
            "consensus_fraction": self.consensus_fraction,
            "candidate_validation_pass_rate": self.candidate_validation_pass_rate,
            "reasons": list(self.reasons),
        }


@dataclass(frozen=True, slots=True)
class PolicyPromotionReport:
    source_bundle_sha256: str
    walk_forward_report_sha256: str
    decomposition_report_sha256: str
    policy_context_sha256: str
    walk_forward_status: WalkForwardStatus
    decomposition_status: DecompositionStatus
    guardrails: PolicyPromotionGuardrails
    calibration_candidate_support: tuple[CalibrationCandidateSupport, ...]
    decision: PolicyPromotionDecision

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "calibration_candidate_support",
            tuple(self.calibration_candidate_support),
        )
        for name in (
            "source_bundle_sha256",
            "walk_forward_report_sha256",
            "decomposition_report_sha256",
            "policy_context_sha256",
        ):
            _validate_sha256(getattr(self, name), name)
        if not isinstance(self.walk_forward_status, WalkForwardStatus):
            raise ValueError("walk_forward_status has invalid type")
        if not isinstance(self.decomposition_status, DecompositionStatus):
            raise ValueError("decomposition_status has invalid type")
        if not isinstance(self.guardrails, PolicyPromotionGuardrails):
            raise ValueError("guardrails has invalid type")
        if not isinstance(self.decision, PolicyPromotionDecision):
            raise ValueError("decision has invalid type")
        keys = [_candidate_key(item.candidate) for item in self.calibration_candidate_support]
        if keys != sorted(keys) or len(set(keys)) != len(keys):
            raise ValueError("calibration candidate support must be uniquely sorted")
        if sum(item.support_count for item in self.calibration_candidate_support) != self.decision.selected_policy_folds:
            raise ValueError("promotion decision selected-policy count differs from support evidence")

    def canonical_payload(self) -> dict[str, Any]:
        return {
            "schema": _PROMOTION_SCHEMA,
            "source_bundle_sha256": self.source_bundle_sha256,
            "walk_forward_report_sha256": self.walk_forward_report_sha256,
            "decomposition_report_sha256": self.decomposition_report_sha256,
            "policy_context_sha256": self.policy_context_sha256,
            "walk_forward_status": self.walk_forward_status.value,
            "decomposition_status": self.decomposition_status.value,
            "guardrails": self.guardrails.to_payload(),
            "calibration_candidate_support": [
                item.to_payload() for item in self.calibration_candidate_support
            ],
            "decision": self.decision.to_payload(),
            "candidate_selection_source": "walk_forward_calibration_selections_only",
            "validation_can_only_veto": True,
            "decomposition_never_selects_or_mutates_policy": True,
            "promotion_is_not_live_execution": True,
            "advisory_paper_only": True,
        }

    @property
    def sha256(self) -> str:
        return _sha256(self.canonical_payload())

    def to_envelope(self) -> dict[str, Any]:
        return {"payload": self.canonical_payload(), "sha256": self.sha256}


def _build_candidate_support(
    walk_forward_report: WalkForwardReport,
) -> tuple[CalibrationCandidateSupport, ...]:
    grouped: dict[
        tuple[float, float],
        dict[str, Any],
    ] = defaultdict(lambda: {"candidate": None, "folds": [], "passed": [], "failed": []})
    for fold in walk_forward_report.folds:
        candidate = fold.selected_candidate
        if candidate is None:
            continue
        key = _candidate_key(candidate)
        row = grouped[key]
        row["candidate"] = candidate
        row["folds"].append(fold.plan.index)
        if fold.passed:
            row["passed"].append(fold.plan.index)
        else:
            row["failed"].append(fold.plan.index)
    support = []
    for key in sorted(grouped):
        row = grouped[key]
        support.append(
            CalibrationCandidateSupport(
                candidate=row["candidate"],
                fold_indexes=tuple(row["folds"]),
                validation_passed_fold_indexes=tuple(row["passed"]),
                validation_failed_fold_indexes=tuple(row["failed"]),
            )
        )
    return tuple(support)


def _decision_for_support(
    walk_forward_status: WalkForwardStatus,
    decomposition_status: DecompositionStatus,
    support: Sequence[CalibrationCandidateSupport],
    guardrails: PolicyPromotionGuardrails,
) -> PolicyPromotionDecision:
    selected_policy_folds = sum(item.support_count for item in support)

    def without_candidate(status: PolicyPromotionStatus, reason: str) -> PolicyPromotionDecision:
        return PolicyPromotionDecision(
            status=status,
            candidate=None,
            selected_policy_folds=selected_policy_folds,
            supporting_fold_indexes=(),
            validation_passed_fold_indexes=(),
            validation_failed_fold_indexes=(),
            consensus_fraction=None,
            candidate_validation_pass_rate=None,
            reasons=(reason,),
        )

    if walk_forward_status is not WalkForwardStatus.PASSED_STABILITY:
        return without_candidate(
            PolicyPromotionStatus.BLOCKED_WALK_FORWARD,
            "walk-forward evidence did not pass temporal stability",
        )
    if decomposition_status is not DecompositionStatus.STABLE_BASELINE:
        return without_candidate(
            PolicyPromotionStatus.BLOCKED_DECOMPOSITION,
            "stability decomposition is not a verified stable baseline",
        )
    if selected_policy_folds < guardrails.min_selected_policy_folds:
        return without_candidate(
            PolicyPromotionStatus.INSUFFICIENT_SELECTED_POLICIES,
            "too few walk-forward calibration folds selected a policy",
        )
    if not support:
        return without_candidate(
            PolicyPromotionStatus.INSUFFICIENT_SELECTED_POLICIES,
            "walk-forward evidence selected no calibration policy",
        )

    max_support = max(item.support_count for item in support)
    winners = tuple(item for item in support if item.support_count == max_support)
    if len(winners) != 1:
        return without_candidate(
            PolicyPromotionStatus.AMBIGUOUS_CALIBRATION_CONSENSUS,
            "calibration-selected policy consensus has an exact support tie",
        )

    winner = winners[0]
    consensus_fraction = winner.support_count / selected_policy_folds
    decision_kwargs = {
        "candidate": winner.candidate,
        "selected_policy_folds": selected_policy_folds,
        "supporting_fold_indexes": winner.fold_indexes,
        "validation_passed_fold_indexes": winner.validation_passed_fold_indexes,
        "validation_failed_fold_indexes": winner.validation_failed_fold_indexes,
        "consensus_fraction": consensus_fraction,
        "candidate_validation_pass_rate": winner.validation_pass_rate,
    }
    if winner.support_count < guardrails.min_candidate_supporting_folds:
        return PolicyPromotionDecision(
            status=PolicyPromotionStatus.INSUFFICIENT_CANDIDATE_SUPPORT,
            reasons=("calibration-consensus candidate lacks the required fold support",),
            **decision_kwargs,
        )
    if consensus_fraction < guardrails.min_consensus_fraction:
        return PolicyPromotionDecision(
            status=PolicyPromotionStatus.CONSENSUS_BELOW_FLOOR,
            reasons=("calibration-consensus fraction is below the promotion floor",),
            **decision_kwargs,
        )
    if winner.validation_pass_rate < guardrails.min_candidate_validation_pass_rate:
        return PolicyPromotionDecision(
            status=PolicyPromotionStatus.CANDIDATE_VALIDATION_BELOW_FLOOR,
            reasons=(
                "the calibration-consensus candidate failed the validation veto floor; no fallback candidate is selected",
            ),
            **decision_kwargs,
        )
    return PolicyPromotionDecision(
        status=PolicyPromotionStatus.PROMOTED,
        reasons=(
            "calibration-only policy consensus passed temporal stability and validation veto guardrails",
        ),
        **decision_kwargs,
    )


def run_policy_promotion(
    bundle: ReplayBundle,
    walk_forward_report: WalkForwardReport,
    decomposition_report: StabilityDecompositionReport,
    guardrails: PolicyPromotionGuardrails | None = None,
) -> PolicyPromotionReport:
    active = guardrails or PolicyPromotionGuardrails()
    verify_stability_decomposition_bundle_binding(
        decomposition_report,
        walk_forward_report,
        bundle,
    )
    support = _build_candidate_support(walk_forward_report)
    decision = _decision_for_support(
        walk_forward_report.status,
        decomposition_report.status,
        support,
        active,
    )
    return PolicyPromotionReport(
        source_bundle_sha256=bundle.sha256,
        walk_forward_report_sha256=walk_forward_report.sha256,
        decomposition_report_sha256=decomposition_report.sha256,
        policy_context_sha256=walk_forward_report.policy_context.sha256,
        walk_forward_status=walk_forward_report.status,
        decomposition_status=decomposition_report.status,
        guardrails=active,
        calibration_candidate_support=support,
        decision=decision,
    )


def _support_from_payload(payload: Mapping[str, Any]) -> CalibrationCandidateSupport:
    expected_keys = {
        "candidate",
        "fold_indexes",
        "validation_passed_fold_indexes",
        "validation_failed_fold_indexes",
        "support_count",
        "validation_pass_rate",
    }
    if set(payload) != expected_keys:
        raise ValueError("promotion candidate support fields are not canonical")
    candidate_payload = payload["candidate"]
    if not isinstance(candidate_payload, dict) or set(candidate_payload) != {
        "execute_net_edge_bps",
        "volatile_return_bps",
    }:
        raise ValueError("promotion candidate payload is invalid")
    candidate = JointPolicyCandidate(**candidate_payload)
    row = CalibrationCandidateSupport(
        candidate=candidate,
        fold_indexes=tuple(payload["fold_indexes"]),
        validation_passed_fold_indexes=tuple(payload["validation_passed_fold_indexes"]),
        validation_failed_fold_indexes=tuple(payload["validation_failed_fold_indexes"]),
    )
    if payload["support_count"] != row.support_count:
        raise ValueError("promotion candidate support_count does not match fold evidence")
    if payload["validation_pass_rate"] != row.validation_pass_rate:
        raise ValueError("promotion candidate validation_pass_rate does not match fold evidence")
    return row


def verify_policy_promotion_report_envelope(
    envelope: Mapping[str, Any],
) -> dict[str, Any]:
    try:
        payload = envelope["payload"]
        supplied_sha = envelope["sha256"]
    except KeyError as exc:
        raise ValueError("policy promotion envelope is incomplete") from exc
    if not isinstance(payload, dict) or not isinstance(supplied_sha, str):
        raise ValueError("policy promotion envelope has invalid types")
    expected_keys = {
        "schema",
        "source_bundle_sha256",
        "walk_forward_report_sha256",
        "decomposition_report_sha256",
        "policy_context_sha256",
        "walk_forward_status",
        "decomposition_status",
        "guardrails",
        "calibration_candidate_support",
        "decision",
        "candidate_selection_source",
        "validation_can_only_veto",
        "decomposition_never_selects_or_mutates_policy",
        "promotion_is_not_live_execution",
        "advisory_paper_only",
    }
    if set(payload) != expected_keys:
        raise ValueError("policy promotion payload fields are not canonical")
    if payload.get("schema") != _PROMOTION_SCHEMA:
        raise ValueError("unsupported policy promotion schema")
    for name in (
        "source_bundle_sha256",
        "walk_forward_report_sha256",
        "decomposition_report_sha256",
        "policy_context_sha256",
    ):
        _validate_sha256(payload.get(name), name)
    if payload.get("candidate_selection_source") != "walk_forward_calibration_selections_only":
        raise ValueError("policy promotion candidate-selection source is invalid")
    for key in (
        "validation_can_only_veto",
        "decomposition_never_selects_or_mutates_policy",
        "promotion_is_not_live_execution",
        "advisory_paper_only",
    ):
        if payload.get(key) is not True:
            raise ValueError(f"policy promotion invariant flag is invalid: {key}")
    try:
        walk_status = WalkForwardStatus(payload["walk_forward_status"])
        decomposition_status = DecompositionStatus(payload["decomposition_status"])
    except ValueError as exc:
        raise ValueError("policy promotion upstream status is invalid") from exc
    if not isinstance(payload.get("guardrails"), dict):
        raise ValueError("policy promotion guardrails must be an object")
    guardrails = PolicyPromotionGuardrails(**payload["guardrails"])
    support_payload = payload.get("calibration_candidate_support")
    if not isinstance(support_payload, list):
        raise ValueError("policy promotion candidate support must be a list")
    support = tuple(_support_from_payload(item) for item in support_payload)
    keys = [_candidate_key(item.candidate) for item in support]
    if keys != sorted(keys) or len(keys) != len(set(keys)):
        raise ValueError("policy promotion candidate support is not uniquely sorted")
    expected_decision = _decision_for_support(
        walk_status,
        decomposition_status,
        support,
        guardrails,
    ).to_payload()
    if payload.get("decision") != expected_decision:
        raise ValueError("policy promotion decision does not match bound support evidence")
    digest = _sha256(payload)
    if not hmac.compare_digest(digest, supplied_sha):
        raise ValueError("policy promotion SHA-256 does not match payload")
    _canonical_json(payload)
    return dict(payload)


def verify_policy_promotion_bundle_binding(
    report: PolicyPromotionReport,
    walk_forward_report: WalkForwardReport,
    decomposition_report: StabilityDecompositionReport,
    bundle: ReplayBundle,
) -> bool:
    verify_policy_promotion_report_envelope(report.to_envelope())
    if report.source_bundle_sha256 != bundle.sha256:
        raise ValueError("policy promotion source bundle SHA-256 does not match bundle")
    if report.walk_forward_report_sha256 != walk_forward_report.sha256:
        raise ValueError("policy promotion walk-forward SHA-256 does not match report")
    if report.decomposition_report_sha256 != decomposition_report.sha256:
        raise ValueError("policy promotion decomposition SHA-256 does not match report")
    if report.policy_context_sha256 != walk_forward_report.policy_context.sha256:
        raise ValueError("policy promotion policy-context SHA-256 does not match walk-forward context")
    rebuilt = run_policy_promotion(
        bundle,
        walk_forward_report,
        decomposition_report,
        report.guardrails,
    )
    if rebuilt.canonical_payload() != report.canonical_payload():
        raise ValueError("policy promotion report does not reproduce from evidence")
    return True
