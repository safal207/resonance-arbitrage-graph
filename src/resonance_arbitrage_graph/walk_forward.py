from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, replace
from enum import Enum
import hashlib
import hmac
import json
import math
from typing import Any

from .joint_holdout import (
    JointCandidateGrid,
    JointHoldoutPolicy,
    JointHoldoutReport,
    JointHoldoutStatus,
    JointPolicyCandidate,
    JointPolicyContext,
    run_joint_holdout_calibration,
    validate_joint_policy_context,
    verify_joint_holdout_report_envelope,
)
from .replay import ReplayBundle, ReplayCase


_WALK_FORWARD_REPORT_SCHEMA = "resonance.arbitrage.walk-forward-report/v0.1"


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


class WalkForwardStatus(str, Enum):
    PASSED_STABILITY = "PASSED_STABILITY"
    INSUFFICIENT_CORPUS = "INSUFFICIENT_CORPUS"
    INSUFFICIENT_FOLDS = "INSUFFICIENT_FOLDS"
    UNSTABLE = "UNSTABLE"


@dataclass(frozen=True, slots=True)
class WalkForwardPolicy:
    joint_policy: JointHoldoutPolicy
    initial_calibration_operations: int
    validation_operations: int
    min_folds: int = 3
    min_selected_policy_folds: int = 2
    min_validation_pass_rate: float = 2.0 / 3.0
    max_policy_switch_rate: float = 0.5

    def __post_init__(self) -> None:
        if not isinstance(self.joint_policy, JointHoldoutPolicy):
            raise ValueError("joint_policy must be JointHoldoutPolicy")
        if self.initial_calibration_operations < self.joint_policy.holdout.min_calibration_operations:
            raise ValueError(
                "initial_calibration_operations must satisfy joint holdout calibration minimum"
            )
        if self.validation_operations < self.joint_policy.holdout.min_validation_operations:
            raise ValueError(
                "validation_operations must satisfy joint holdout validation minimum"
            )
        if self.min_folds < 2:
            raise ValueError("min_folds must be >= 2")
        if self.min_selected_policy_folds < 2:
            raise ValueError("min_selected_policy_folds must be >= 2")
        if self.min_selected_policy_folds > self.min_folds:
            raise ValueError("min_selected_policy_folds cannot exceed min_folds")
        for name in ("min_validation_pass_rate", "max_policy_switch_rate"):
            value = getattr(self, name)
            if not math.isfinite(value) or not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be finite and in [0, 1]")

    def to_payload(self) -> dict[str, Any]:
        return {
            "joint_policy": self.joint_policy.to_payload(),
            "initial_calibration_operations": self.initial_calibration_operations,
            "validation_operations": self.validation_operations,
            "min_folds": self.min_folds,
            "min_selected_policy_folds": self.min_selected_policy_folds,
            "min_validation_pass_rate": self.min_validation_pass_rate,
            "max_policy_switch_rate": self.max_policy_switch_rate,
        }


@dataclass(frozen=True, slots=True)
class _OperationRow:
    detected_at_ms: int
    available_at_ms: int
    logical_operation_id: str
    cases: tuple[ReplayCase, ...]


def _operation_rows(bundle: ReplayBundle) -> tuple[_OperationRow, ...]:
    grouped: dict[str, list[ReplayCase]] = defaultdict(list)
    for case in bundle.cases:
        grouped[case.logical_operation_id].append(case)
    rows: list[_OperationRow] = []
    for operation_id, cases in grouped.items():
        ordered = tuple(sorted(cases, key=lambda item: item.attempt))
        detected_at = ordered[0].detected_at_ms
        if any(case.detected_at_ms != detected_at for case in ordered):
            raise ValueError("logical operation detection time drifted")
        rows.append(
            _OperationRow(
                detected_at_ms=detected_at,
                available_at_ms=max(case.outcome.observed_at_ms for case in ordered),
                logical_operation_id=operation_id,
                cases=ordered,
            )
        )
    rows.sort(key=lambda row: (row.detected_at_ms, row.logical_operation_id))
    return tuple(rows)


def _prefix_availability(rows: Sequence[_OperationRow]) -> tuple[int, ...]:
    running = -1
    values: list[int] = []
    for row in rows:
        running = max(running, row.available_at_ms)
        values.append(running)
    return tuple(values)


def _is_causal_boundary(
    rows: Sequence[_OperationRow],
    prefix_available_at_ms: Sequence[int],
    cut: int,
) -> bool:
    if cut <= 0 or cut >= len(rows):
        return False
    return (
        rows[cut - 1].detected_at_ms < rows[cut].detected_at_ms
        and prefix_available_at_ms[cut - 1] < rows[cut].detected_at_ms
    )


def _first_causal_cut(
    rows: Sequence[_OperationRow],
    prefix_available_at_ms: Sequence[int],
    minimum_cut: int,
) -> int | None:
    for cut in range(max(1, minimum_cut), len(rows)):
        if _is_causal_boundary(rows, prefix_available_at_ms, cut):
            return cut
    return None


@dataclass(frozen=True, slots=True)
class WalkForwardFoldPlan:
    index: int
    calibration_operation_ids: tuple[str, ...]
    validation_operation_ids: tuple[str, ...]
    calibration_max_detected_at_ms: int
    calibration_max_observed_at_ms: int
    validation_min_detected_at_ms: int
    validation_max_detected_at_ms: int
    validation_max_observed_at_ms: int

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "calibration_operation_ids", tuple(self.calibration_operation_ids)
        )
        object.__setattr__(
            self, "validation_operation_ids", tuple(self.validation_operation_ids)
        )
        if self.index < 1:
            raise ValueError("walk-forward fold index must be >= 1")
        if not self.calibration_operation_ids or not self.validation_operation_ids:
            raise ValueError("walk-forward fold requires calibration and validation operations")
        if len(set(self.calibration_operation_ids)) != len(self.calibration_operation_ids):
            raise ValueError("duplicate calibration logical operation in walk-forward fold")
        if len(set(self.validation_operation_ids)) != len(self.validation_operation_ids):
            raise ValueError("duplicate validation logical operation in walk-forward fold")
        if set(self.calibration_operation_ids) & set(self.validation_operation_ids):
            raise ValueError("logical operation leaked across walk-forward fold")
        if self.calibration_max_detected_at_ms >= self.validation_min_detected_at_ms:
            raise ValueError("walk-forward validation must be strictly later than calibration")
        if self.calibration_max_observed_at_ms >= self.validation_min_detected_at_ms:
            raise ValueError(
                "calibration outcome was not available before walk-forward validation began"
            )
        if self.validation_min_detected_at_ms > self.validation_max_detected_at_ms:
            raise ValueError("walk-forward validation timestamp range is invalid")

    def to_payload(self) -> dict[str, Any]:
        return {
            "index": self.index,
            "calibration_operation_ids": list(self.calibration_operation_ids),
            "validation_operation_ids": list(self.validation_operation_ids),
            "calibration_max_detected_at_ms": self.calibration_max_detected_at_ms,
            "calibration_max_observed_at_ms": self.calibration_max_observed_at_ms,
            "validation_min_detected_at_ms": self.validation_min_detected_at_ms,
            "validation_max_detected_at_ms": self.validation_max_detected_at_ms,
            "validation_max_observed_at_ms": self.validation_max_observed_at_ms,
        }


@dataclass(frozen=True, slots=True)
class WalkForwardPlan:
    source_operation_ids: tuple[str, ...]
    folds: tuple[WalkForwardFoldPlan, ...]
    unused_tail_operation_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "source_operation_ids", tuple(self.source_operation_ids))
        object.__setattr__(self, "folds", tuple(self.folds))
        object.__setattr__(
            self, "unused_tail_operation_ids", tuple(self.unused_tail_operation_ids)
        )
        if len(set(self.source_operation_ids)) != len(self.source_operation_ids):
            raise ValueError("walk-forward source operations must be unique")
        if not self.folds:
            if self.unused_tail_operation_ids != self.source_operation_ids:
                raise ValueError("empty walk-forward plan must expose the full unused corpus")
            return
        consumed = self.folds[0].calibration_operation_ids
        if self.source_operation_ids[: len(consumed)] != consumed:
            raise ValueError("walk-forward calibration is not a source-corpus prefix")
        for expected_index, fold in enumerate(self.folds, start=1):
            if fold.index != expected_index:
                raise ValueError("walk-forward fold indexes are not contiguous")
            if fold.calibration_operation_ids != consumed:
                raise ValueError("walk-forward calibration must expand by prior validation")
            start = len(consumed)
            end = start + len(fold.validation_operation_ids)
            if self.source_operation_ids[start:end] != fold.validation_operation_ids:
                raise ValueError("walk-forward validation is not the next source-corpus slice")
            consumed = consumed + fold.validation_operation_ids
        if self.source_operation_ids[len(consumed) :] != self.unused_tail_operation_ids:
            raise ValueError("walk-forward unused tail does not match source corpus suffix")

    def to_payload(self) -> dict[str, Any]:
        return {
            "source_operation_ids": list(self.source_operation_ids),
            "folds": [fold.to_payload() for fold in self.folds],
            "unused_tail_operation_ids": list(self.unused_tail_operation_ids),
        }


def plan_walk_forward_folds(
    bundle: ReplayBundle,
    policy: WalkForwardPolicy,
) -> WalkForwardPlan:
    rows = _operation_rows(bundle)
    source_ids = tuple(row.logical_operation_id for row in rows)
    prefix_available = _prefix_availability(rows)
    minimum_total = policy.initial_calibration_operations + policy.validation_operations
    if len(rows) < minimum_total:
        return WalkForwardPlan(source_ids, (), source_ids)
    calibration_end = _first_causal_cut(
        rows,
        prefix_available,
        policy.initial_calibration_operations,
    )
    if calibration_end is None:
        return WalkForwardPlan(source_ids, (), source_ids)
    folds: list[WalkForwardFoldPlan] = []
    while len(rows) - calibration_end >= policy.validation_operations:
        target_validation_end = calibration_end + policy.validation_operations
        if target_validation_end >= len(rows):
            validation_end = len(rows)
        else:
            validation_end = _first_causal_cut(
                rows,
                prefix_available,
                target_validation_end,
            )
            if validation_end is None:
                validation_end = len(rows)
        calibration_rows = rows[:calibration_end]
        validation_rows = rows[calibration_end:validation_end]
        if len(validation_rows) < policy.validation_operations:
            break
        folds.append(
            WalkForwardFoldPlan(
                index=len(folds) + 1,
                calibration_operation_ids=tuple(
                    row.logical_operation_id for row in calibration_rows
                ),
                validation_operation_ids=tuple(
                    row.logical_operation_id for row in validation_rows
                ),
                calibration_max_detected_at_ms=calibration_rows[-1].detected_at_ms,
                calibration_max_observed_at_ms=max(
                    row.available_at_ms for row in calibration_rows
                ),
                validation_min_detected_at_ms=validation_rows[0].detected_at_ms,
                validation_max_detected_at_ms=validation_rows[-1].detected_at_ms,
                validation_max_observed_at_ms=max(
                    row.available_at_ms for row in validation_rows
                ),
            )
        )
        if validation_end == len(rows):
            calibration_end = validation_end
            break
        calibration_end = validation_end
    consumed = 0
    if folds:
        consumed = (
            len(folds[-1].calibration_operation_ids)
            + len(folds[-1].validation_operation_ids)
        )
    return WalkForwardPlan(
        source_operation_ids=source_ids,
        folds=tuple(folds),
        unused_tail_operation_ids=source_ids[consumed:],
    )


def _subset_bundle(bundle: ReplayBundle, operation_ids: Sequence[str]) -> ReplayBundle:
    wanted = set(operation_ids)
    cases = tuple(
        case for case in bundle.cases if case.logical_operation_id in wanted
    )
    present = {case.logical_operation_id for case in cases}
    if present != wanted:
        raise ValueError("walk-forward subset is missing logical operations")
    return ReplayBundle(cases=cases)


def _forced_fold_policy(
    policy: JointHoldoutPolicy,
    *,
    calibration_operations: int,
    validation_operations: int,
) -> JointHoldoutPolicy:
    total = calibration_operations + validation_operations
    holdout = replace(
        policy.holdout,
        validation_fraction=validation_operations / total,
        min_calibration_operations=calibration_operations,
        min_validation_operations=validation_operations,
    )
    return replace(policy, holdout=holdout)


@dataclass(frozen=True, slots=True)
class WalkForwardFold:
    plan: WalkForwardFoldPlan
    fold_bundle_sha256: str
    joint_report: JointHoldoutReport

    def __post_init__(self) -> None:
        if not isinstance(self.plan, WalkForwardFoldPlan):
            raise ValueError("walk-forward fold plan has invalid type")
        if not isinstance(self.joint_report, JointHoldoutReport):
            raise ValueError("walk-forward fold joint_report has invalid type")
        if self.joint_report.source_bundle_sha256 != self.fold_bundle_sha256:
            raise ValueError("walk-forward fold report is not bound to fold bundle")
        if self.joint_report.split is None:
            raise ValueError("walk-forward fold requires an explicit joint holdout split")
        split = self.joint_report.split
        if tuple(split["calibration_operation_ids"]) != self.plan.calibration_operation_ids:
            raise ValueError("walk-forward calibration split does not match fold plan")
        if tuple(split["validation_operation_ids"]) != self.plan.validation_operation_ids:
            raise ValueError("walk-forward validation split does not match fold plan")
        if split["calibration_max_detected_at_ms"] != self.plan.calibration_max_detected_at_ms:
            raise ValueError("walk-forward calibration timestamp does not match fold plan")
        if split["validation_min_detected_at_ms"] != self.plan.validation_min_detected_at_ms:
            raise ValueError("walk-forward validation timestamp does not match fold plan")

    @property
    def passed(self) -> bool:
        return self.joint_report.status is JointHoldoutStatus.PASSED_HOLDOUT

    @property
    def selected_candidate(self) -> JointPolicyCandidate | None:
        return self.joint_report.selected_candidate

    def to_payload(self) -> dict[str, Any]:
        return {
            "plan": self.plan.to_payload(),
            "fold_bundle_sha256": self.fold_bundle_sha256,
            "joint_report": self.joint_report.to_envelope(),
        }


@dataclass(frozen=True, slots=True)
class WalkForwardMetrics:
    total_folds: int
    passed_folds: int
    failed_folds: int
    validation_pass_rate: float | None
    selected_policy_folds: int
    selected_policy_coverage: float | None
    unique_selected_policies: int
    policy_switches: int
    policy_switch_rate: float | None
    min_execute_net_edge_bps: float | None
    max_execute_net_edge_bps: float | None
    min_volatile_return_bps: float | None
    max_volatile_return_bps: float | None

    def to_payload(self) -> dict[str, Any]:
        return {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
        }


def _candidate_switch_metrics(
    candidates: Sequence[JointPolicyCandidate | None],
) -> tuple[int, int, float | None, float | None, float | None, float | None, float | None]:
    selected = [candidate for candidate in candidates if candidate is not None]
    keys = [
        (candidate.execute_net_edge_bps, candidate.volatile_return_bps)
        for candidate in selected
    ]
    switches = sum(left != right for left, right in zip(keys, keys[1:]))
    switch_rate = switches / (len(keys) - 1) if len(keys) >= 2 else None
    if not selected:
        return 0, 0, None, None, None, None, None
    execute = [candidate.execute_net_edge_bps for candidate in selected]
    volatile = [candidate.volatile_return_bps for candidate in selected]
    return (
        len(set(keys)),
        switches,
        switch_rate,
        min(execute),
        max(execute),
        min(volatile),
        max(volatile),
    )


def calculate_walk_forward_metrics(
    folds: Sequence[WalkForwardFold],
) -> WalkForwardMetrics:
    total = len(folds)
    passed = sum(fold.passed for fold in folds)
    candidates = [fold.selected_candidate for fold in folds]
    selected_count = sum(candidate is not None for candidate in candidates)
    unique, switches, switch_rate, min_execute, max_execute, min_volatile, max_volatile = (
        _candidate_switch_metrics(candidates)
    )
    return WalkForwardMetrics(
        total_folds=total,
        passed_folds=passed,
        failed_folds=total - passed,
        validation_pass_rate=passed / total if total else None,
        selected_policy_folds=selected_count,
        selected_policy_coverage=selected_count / total if total else None,
        unique_selected_policies=unique,
        policy_switches=switches,
        policy_switch_rate=switch_rate,
        min_execute_net_edge_bps=min_execute,
        max_execute_net_edge_bps=max_execute,
        min_volatile_return_bps=min_volatile,
        max_volatile_return_bps=max_volatile,
    )


@dataclass(frozen=True, slots=True)
class WalkForwardReport:
    source_bundle_sha256: str
    policy_context: JointPolicyContext
    walk_forward_policy: WalkForwardPolicy
    candidate_grid: JointCandidateGrid
    plan: WalkForwardPlan
    folds: tuple[WalkForwardFold, ...]
    metrics: WalkForwardMetrics
    status: WalkForwardStatus
    reasons: tuple[str, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "folds", tuple(self.folds))
        object.__setattr__(self, "reasons", tuple(self.reasons))
        if len(self.folds) != len(self.plan.folds):
            raise ValueError("walk-forward result count does not match fold plan")
        for planned, executed in zip(self.plan.folds, self.folds):
            if planned != executed.plan:
                raise ValueError("walk-forward executed fold does not match plan")
        if self.metrics.total_folds != len(self.folds):
            raise ValueError("walk-forward metrics fold count is inconsistent")
        if self.status is WalkForwardStatus.PASSED_STABILITY:
            if self.metrics.validation_pass_rate is None:
                raise ValueError("passed walk-forward stability requires validation folds")
            if self.metrics.validation_pass_rate < self.walk_forward_policy.min_validation_pass_rate:
                raise ValueError("passed walk-forward stability violates pass-rate floor")
            if self.metrics.selected_policy_folds < self.walk_forward_policy.min_selected_policy_folds:
                raise ValueError("passed walk-forward stability lacks selected-policy support")
            if (
                self.metrics.policy_switch_rate is None
                or self.metrics.policy_switch_rate > self.walk_forward_policy.max_policy_switch_rate
            ):
                raise ValueError("passed walk-forward stability violates switch-rate ceiling")

    def canonical_payload(self) -> dict[str, Any]:
        return {
            "schema": _WALK_FORWARD_REPORT_SCHEMA,
            "source_bundle_sha256": self.source_bundle_sha256,
            "policy_context": self.policy_context.to_payload(),
            "walk_forward_policy": self.walk_forward_policy.to_payload(),
            "candidate_grid": self.candidate_grid.to_payload(),
            "plan": self.plan.to_payload(),
            "folds": [fold.to_payload() for fold in self.folds],
            "metrics": self.metrics.to_payload(),
            "status": self.status.value,
            "reasons": list(self.reasons),
            "strict_outcome_availability_firewall": True,
            "validation_never_selects_policy": True,
            "advisory_only": True,
        }

    @property
    def sha256(self) -> str:
        return _sha256(self.canonical_payload())

    def to_envelope(self) -> dict[str, Any]:
        return {"payload": self.canonical_payload(), "sha256": self.sha256}


def _verify_plan_payload(plan: Any) -> None:
    if not isinstance(plan, dict):
        raise ValueError("walk-forward plan must be an object")
    if set(plan) != {"source_operation_ids", "folds", "unused_tail_operation_ids"}:
        raise ValueError("walk-forward plan fields are not canonical")
    source = plan["source_operation_ids"]
    folds = plan["folds"]
    tail = plan["unused_tail_operation_ids"]
    if not isinstance(source, list) or not isinstance(folds, list) or not isinstance(tail, list):
        raise ValueError("walk-forward plan has invalid field types")
    if len(set(source)) != len(source):
        raise ValueError("walk-forward plan source operations are not unique")
    consumed: list[str] = []
    for expected_index, fold in enumerate(folds, start=1):
        if not isinstance(fold, dict):
            raise ValueError("walk-forward fold plan must be an object")
        expected_keys = {
            "index",
            "calibration_operation_ids",
            "validation_operation_ids",
            "calibration_max_detected_at_ms",
            "calibration_max_observed_at_ms",
            "validation_min_detected_at_ms",
            "validation_max_detected_at_ms",
            "validation_max_observed_at_ms",
        }
        if set(fold) != expected_keys or fold["index"] != expected_index:
            raise ValueError("walk-forward fold plan is not canonical")
        calibration_ids = fold["calibration_operation_ids"]
        validation_ids = fold["validation_operation_ids"]
        if expected_index == 1:
            consumed = list(calibration_ids)
            if source[: len(consumed)] != consumed:
                raise ValueError("walk-forward first calibration is not source prefix")
        elif calibration_ids != consumed:
            raise ValueError("walk-forward calibration does not expand chronologically")
        if set(calibration_ids) & set(validation_ids):
            raise ValueError("walk-forward fold leaks logical operation across split")
        start = len(consumed)
        end = start + len(validation_ids)
        if source[start:end] != validation_ids:
            raise ValueError("walk-forward validation is not next source slice")
        if fold["calibration_max_detected_at_ms"] >= fold["validation_min_detected_at_ms"]:
            raise ValueError("walk-forward detected-time boundary is not strict")
        if fold["calibration_max_observed_at_ms"] >= fold["validation_min_detected_at_ms"]:
            raise ValueError("walk-forward outcome-availability firewall is invalid")
        consumed.extend(validation_ids)
    if source[len(consumed) :] != tail:
        raise ValueError("walk-forward unused tail is not source suffix")


def verify_walk_forward_report_envelope(
    envelope: Mapping[str, Any],
) -> dict[str, Any]:
    try:
        payload = envelope["payload"]
        supplied_sha = envelope["sha256"]
    except KeyError as exc:
        raise ValueError("walk-forward report envelope is incomplete") from exc
    if not isinstance(payload, dict) or not isinstance(supplied_sha, str):
        raise ValueError("walk-forward report envelope has invalid types")
    expected_keys = {
        "schema",
        "source_bundle_sha256",
        "policy_context",
        "walk_forward_policy",
        "candidate_grid",
        "plan",
        "folds",
        "metrics",
        "status",
        "reasons",
        "strict_outcome_availability_firewall",
        "validation_never_selects_policy",
        "advisory_only",
    }
    if set(payload) != expected_keys:
        raise ValueError("walk-forward report payload fields are not canonical")
    if payload.get("schema") != _WALK_FORWARD_REPORT_SCHEMA:
        raise ValueError("unsupported walk-forward report schema")
    if payload.get("status") not in {status.value for status in WalkForwardStatus}:
        raise ValueError("walk-forward report status is invalid")
    if payload.get("strict_outcome_availability_firewall") is not True:
        raise ValueError("walk-forward outcome-availability firewall flag is invalid")
    if payload.get("validation_never_selects_policy") is not True:
        raise ValueError("walk-forward validation-selection firewall flag is invalid")
    if payload.get("advisory_only") is not True:
        raise ValueError("walk-forward report must remain advisory-only")
    context = payload.get("policy_context")
    if not isinstance(context, dict) or not isinstance(context.get("sha256"), str):
        raise ValueError("walk-forward policy_context has invalid types")
    if not isinstance(context.get("frozen_context"), dict):
        raise ValueError("walk-forward frozen policy context must be an object")
    if not hmac.compare_digest(_sha256(context["frozen_context"]), context["sha256"]):
        raise ValueError("walk-forward policy context SHA-256 does not match frozen context")
    _verify_plan_payload(payload["plan"])
    walk_policy = payload.get("walk_forward_policy")
    if not isinstance(walk_policy, dict) or not isinstance(walk_policy.get("joint_policy"), dict):
        raise ValueError("walk-forward policy payload is invalid")
    base_joint_policy = walk_policy["joint_policy"]
    if not isinstance(base_joint_policy.get("holdout"), dict):
        raise ValueError("walk-forward joint policy payload is invalid")
    folds = payload.get("folds")
    if not isinstance(folds, list) or len(folds) != len(payload["plan"]["folds"]):
        raise ValueError("walk-forward fold results do not match plan")
    nested_payloads: list[dict[str, Any]] = []
    for planned, fold in zip(payload["plan"]["folds"], folds):
        if not isinstance(fold, dict) or set(fold) != {"plan", "fold_bundle_sha256", "joint_report"}:
            raise ValueError("walk-forward fold result fields are not canonical")
        if fold["plan"] != planned:
            raise ValueError("walk-forward fold result plan differs from global plan")
        nested = verify_joint_holdout_report_envelope(fold["joint_report"])
        nested_payloads.append(nested)
        if nested.get("source_bundle_sha256") != fold["fold_bundle_sha256"]:
            raise ValueError("walk-forward nested report is not bound to fold bundle")
        if nested.get("candidate_grid") != payload.get("candidate_grid"):
            raise ValueError("walk-forward nested candidate grid differs from outer grid")
        if nested.get("policy_context") != payload.get("policy_context"):
            raise ValueError("walk-forward nested policy context differs from outer context")
        split = nested.get("split")
        if not isinstance(split, dict):
            raise ValueError("walk-forward nested report lacks explicit split")
        if split.get("calibration_operation_ids") != planned["calibration_operation_ids"]:
            raise ValueError("walk-forward nested calibration split differs from plan")
        if split.get("validation_operation_ids") != planned["validation_operation_ids"]:
            raise ValueError("walk-forward nested validation split differs from plan")
        nested_policy = nested.get("joint_policy")
        if not isinstance(nested_policy, dict) or not isinstance(nested_policy.get("holdout"), dict):
            raise ValueError("walk-forward nested joint policy payload is invalid")
        nested_holdout = dict(nested_policy["holdout"])
        cal_count = len(planned["calibration_operation_ids"])
        val_count = len(planned["validation_operation_ids"])
        expected_fraction = val_count / (cal_count + val_count)
        if nested_holdout.get("min_calibration_operations") != cal_count:
            raise ValueError("walk-forward nested calibration size differs from fold plan")
        if nested_holdout.get("min_validation_operations") != val_count:
            raise ValueError("walk-forward nested validation size differs from fold plan")
        if nested_holdout.get("validation_fraction") != expected_fraction:
            raise ValueError("walk-forward nested validation fraction differs from fold geometry")
        base_compare = dict(base_joint_policy)
        nested_compare = dict(nested_policy)
        base_holdout = dict(base_compare["holdout"])
        for key in ("validation_fraction", "min_calibration_operations", "min_validation_operations"):
            base_holdout.pop(key, None)
            nested_holdout.pop(key, None)
        base_compare["holdout"] = base_holdout
        nested_compare["holdout"] = nested_holdout
        if nested_compare != base_compare:
            raise ValueError("walk-forward nested guardrails drifted across folds")
    metrics = payload.get("metrics")
    if not isinstance(metrics, dict) or set(metrics) != set(WalkForwardMetrics.__dataclass_fields__):
        raise ValueError("walk-forward metrics fields are not canonical")
    total = len(nested_payloads)
    passed = sum(item["status"] == JointHoldoutStatus.PASSED_HOLDOUT.value for item in nested_payloads)
    selected = [item["selected_candidate"] for item in nested_payloads if item.get("selected_candidate") is not None]
    keys = [(item["execute_net_edge_bps"], item["volatile_return_bps"]) for item in selected]
    switches = sum(left != right for left, right in zip(keys, keys[1:]))
    switch_rate = switches / (len(keys) - 1) if len(keys) >= 2 else None
    execute_values = [item[0] for item in keys]
    volatile_values = [item[1] for item in keys]
    expected_metrics = {
        "total_folds": total,
        "passed_folds": passed,
        "failed_folds": total - passed,
        "validation_pass_rate": passed / total if total else None,
        "selected_policy_folds": len(selected),
        "selected_policy_coverage": len(selected) / total if total else None,
        "unique_selected_policies": len(set(keys)),
        "policy_switches": switches,
        "policy_switch_rate": switch_rate,
        "min_execute_net_edge_bps": min(execute_values) if execute_values else None,
        "max_execute_net_edge_bps": max(execute_values) if execute_values else None,
        "min_volatile_return_bps": min(volatile_values) if volatile_values else None,
        "max_volatile_return_bps": max(volatile_values) if volatile_values else None,
    }
    if metrics != expected_metrics:
        raise ValueError("walk-forward metrics do not match nested fold evidence")
    if payload["status"] == WalkForwardStatus.PASSED_STABILITY.value:
        if total < walk_policy["min_folds"]:
            raise ValueError("passed walk-forward report has insufficient folds")
        if len(selected) < walk_policy["min_selected_policy_folds"]:
            raise ValueError("passed walk-forward report has insufficient selected policies")
        if expected_metrics["validation_pass_rate"] < walk_policy["min_validation_pass_rate"]:
            raise ValueError("passed walk-forward report violates validation pass-rate floor")
        if switch_rate is None or switch_rate > walk_policy["max_policy_switch_rate"]:
            raise ValueError("passed walk-forward report violates policy switch-rate ceiling")
    digest = _sha256(payload)
    if not hmac.compare_digest(digest, supplied_sha):
        raise ValueError("walk-forward report SHA-256 does not match payload")
    _canonical_json(payload)
    return dict(payload)


def _run_fold(
    bundle: ReplayBundle,
    grid: JointCandidateGrid,
    policy: WalkForwardPolicy,
    plan: WalkForwardFoldPlan,
) -> WalkForwardFold:
    operation_ids = plan.calibration_operation_ids + plan.validation_operation_ids
    fold_bundle = _subset_bundle(bundle, operation_ids)
    fold_policy = _forced_fold_policy(
        policy.joint_policy,
        calibration_operations=len(plan.calibration_operation_ids),
        validation_operations=len(plan.validation_operation_ids),
    )
    report = run_joint_holdout_calibration(fold_bundle, grid, fold_policy)
    if report.split is None:
        raise RuntimeError("planned walk-forward fold did not produce an explicit split")
    return WalkForwardFold(
        plan=plan,
        fold_bundle_sha256=fold_bundle.sha256,
        joint_report=report,
    )


def run_walk_forward_stability(
    bundle: ReplayBundle,
    grid: JointCandidateGrid,
    policy: WalkForwardPolicy,
) -> WalkForwardReport:
    context = validate_joint_policy_context(bundle)
    for candidate in grid.candidates():
        if candidate.execute_net_edge_bps <= context.observe_net_edge_bps:
            raise ValueError("candidate execute threshold must exceed corpus observe threshold")
    plan = plan_walk_forward_folds(bundle, policy)
    folds = tuple(_run_fold(bundle, grid, policy, item) for item in plan.folds)
    metrics = calculate_walk_forward_metrics(folds)
    reasons: list[str] = []
    minimum_total = policy.initial_calibration_operations + policy.validation_operations
    source_count = len(plan.source_operation_ids)
    if source_count < minimum_total:
        status = WalkForwardStatus.INSUFFICIENT_CORPUS
        reasons.append(
            f"insufficient logical operations for first walk-forward fold: {source_count} < {minimum_total}"
        )
    elif metrics.total_folds < policy.min_folds:
        status = WalkForwardStatus.INSUFFICIENT_FOLDS
        reasons.append(
            f"walk-forward produced {metrics.total_folds} folds < required {policy.min_folds}; strict outcome-availability boundaries may reduce usable folds"
        )
    else:
        if metrics.selected_policy_folds < policy.min_selected_policy_folds:
            reasons.append("INSUFFICIENT_SELECTED_POLICY_FOLDS")
        if metrics.validation_pass_rate is None or metrics.validation_pass_rate < policy.min_validation_pass_rate:
            reasons.append("VALIDATION_PASS_RATE_BELOW_FLOOR")
        if metrics.policy_switch_rate is None or metrics.policy_switch_rate > policy.max_policy_switch_rate:
            reasons.append("POLICY_SWITCH_RATE_ABOVE_CEILING")
        status = WalkForwardStatus.PASSED_STABILITY if not reasons else WalkForwardStatus.UNSTABLE
        if not reasons:
            reasons.append(
                "joint policy calibration remained within temporal validation and policy-switch stability guardrails"
            )
    return WalkForwardReport(
        source_bundle_sha256=bundle.sha256,
        policy_context=context,
        walk_forward_policy=policy,
        candidate_grid=grid,
        plan=plan,
        folds=folds,
        metrics=metrics,
        status=status,
        reasons=tuple(reasons),
    )


def verify_walk_forward_report_bundle_binding(
    report: WalkForwardReport,
    bundle: ReplayBundle,
) -> bool:
    if not isinstance(report, WalkForwardReport):
        raise ValueError("report must be WalkForwardReport")
    if report.source_bundle_sha256 != bundle.sha256:
        raise ValueError("walk-forward report source bundle SHA-256 does not match bundle")
    rebuilt = run_walk_forward_stability(
        bundle,
        report.candidate_grid,
        report.walk_forward_policy,
    )
    if rebuilt.canonical_payload() != report.canonical_payload():
        raise ValueError("walk-forward report does not deterministically reproduce from bundle")
    return True
