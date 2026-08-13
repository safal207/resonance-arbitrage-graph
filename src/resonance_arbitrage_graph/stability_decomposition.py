from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, replace
from enum import Enum
import hashlib
import hmac
import json
import math
from statistics import median
from typing import Any

from .joint_holdout import JointPolicyCandidate
from .replay import ReplayBundle, ReplayCase, ReplayResult, calculate_replay_metrics, replay_case
from .walk_forward import (
    WalkForwardFold,
    WalkForwardReport,
    WalkForwardStatus,
    verify_walk_forward_report_bundle_binding,
)
from .window_regime import derive_window_regime_context


_DECOMPOSITION_SCHEMA = "resonance.arbitrage.stability-decomposition-report/v0.1"
_SPARSE_DIAGNOSTIC_REASON = "fold population is below decomposition minimum"


def _canonical_json(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def _sha256(payload: Any) -> str:
    return hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()


class InstabilityDriver(str, Enum):
    REGIME_DRIFT = "REGIME_DRIFT"
    ROUTE_DRIFT = "ROUTE_DRIFT"
    LIQUIDITY_DETERIORATION = "LIQUIDITY_DETERIORATION"
    FRESHNESS_DETERIORATION = "FRESHNESS_DETERIORATION"
    PREDICTION_BIAS_WORSENING = "PREDICTION_BIAS_WORSENING"
    CAUSAL_SUPPORT_LOSS = "CAUSAL_SUPPORT_LOSS"
    UNEXPLAINED_FAILURE = "UNEXPLAINED_FAILURE"
    INSUFFICIENT_DIAGNOSTIC_EVIDENCE = "INSUFFICIENT_DIAGNOSTIC_EVIDENCE"


class DecompositionStatus(str, Enum):
    STABLE_BASELINE = "STABLE_BASELINE"
    DECOMPOSED_INSTABILITY = "DECOMPOSED_INSTABILITY"
    PARTIALLY_DECOMPOSED = "PARTIALLY_DECOMPOSED"
    UNEXPLAINED_INSTABILITY = "UNEXPLAINED_INSTABILITY"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


@dataclass(frozen=True, slots=True)
class StabilityDecompositionPolicy:
    min_operations_per_side: int = 2
    regime_tv_threshold: float = 0.25
    route_tv_threshold: float = 0.25
    capacity_ratio_drop_fraction_threshold: float = 0.25
    quote_age_increase_ms_threshold: float = 500.0
    overprediction_penalty_increase_bps_threshold: float = 10.0
    causal_support_rate_drop_threshold: float = 0.20

    def __post_init__(self) -> None:
        if self.min_operations_per_side < 1:
            raise ValueError("min_operations_per_side must be >= 1")
        for name in ("regime_tv_threshold", "route_tv_threshold", "capacity_ratio_drop_fraction_threshold", "causal_support_rate_drop_threshold"):
            value = getattr(self, name)
            if not math.isfinite(value) or not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be finite and in [0, 1]")
        for name in ("quote_age_increase_ms_threshold", "overprediction_penalty_increase_bps_threshold"):
            value = getattr(self, name)
            if not math.isfinite(value) or value < 0:
                raise ValueError(f"{name} must be finite and non-negative")

    def to_payload(self) -> dict[str, Any]:
        return {name: getattr(self, name) for name in self.__dataclass_fields__}


@dataclass(frozen=True, slots=True)
class FoldDriftMetrics:
    calibration_operations: int
    validation_operations: int
    regime_tv_distance: float
    route_tv_distance: float
    calibration_median_capacity_ratio: float
    validation_median_capacity_ratio: float
    capacity_ratio_drop_fraction: float
    calibration_median_quote_age_ms: float
    validation_median_quote_age_ms: float
    quote_age_increase_ms: float
    calibration_overprediction_penalty_bps: float | None
    validation_overprediction_penalty_bps: float | None
    overprediction_penalty_increase_bps: float | None
    calibration_execute_support_rate: float
    validation_execute_support_rate: float
    calibration_volatility_support_rate: float
    validation_volatility_support_rate: float
    causal_support_rate_drop: float

    def to_payload(self) -> dict[str, Any]:
        return {name: getattr(self, name) for name in self.__dataclass_fields__}


@dataclass(frozen=True, slots=True)
class FoldDecomposition:
    fold_index: int
    validation_passed: bool
    selected_candidate: JointPolicyCandidate | None
    metrics: FoldDriftMetrics | None
    observed_drivers: tuple[InstabilityDriver, ...]
    attributed_drivers: tuple[InstabilityDriver, ...]
    primary_driver: InstabilityDriver | None
    reasons: tuple[str, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "observed_drivers", tuple(self.observed_drivers))
        object.__setattr__(self, "attributed_drivers", tuple(self.attributed_drivers))
        object.__setattr__(self, "reasons", tuple(self.reasons))
        if self.fold_index < 1:
            raise ValueError("fold_index must be >= 1")
        if self.metrics is None and self.selected_candidate is not None:
            if self.reasons != (_SPARSE_DIAGNOSTIC_REASON,):
                raise ValueError("selected fold without metrics requires explicit sparse diagnostic evidence")
            if self.observed_drivers:
                raise ValueError("sparse selected fold cannot claim observed drift drivers")
            expected_attributed = () if self.validation_passed else (InstabilityDriver.INSUFFICIENT_DIAGNOSTIC_EVIDENCE,)
            if self.attributed_drivers != expected_attributed:
                raise ValueError("sparse selected fold has invalid attributed drivers")
            expected_primary = expected_attributed[0] if expected_attributed else None
            if self.primary_driver is not expected_primary:
                raise ValueError("sparse selected fold has invalid primary driver")
        if self.primary_driver is not None and self.primary_driver not in self.attributed_drivers:
            raise ValueError("primary driver must be one of attributed drivers")

    def to_payload(self) -> dict[str, Any]:
        return {
            "fold_index": self.fold_index,
            "validation_passed": self.validation_passed,
            "selected_candidate": self.selected_candidate.to_payload() if self.selected_candidate else None,
            "metrics": self.metrics.to_payload() if self.metrics else None,
            "observed_drivers": [driver.value for driver in self.observed_drivers],
            "attributed_drivers": [driver.value for driver in self.attributed_drivers],
            "primary_driver": self.primary_driver.value if self.primary_driver else None,
            "reasons": list(self.reasons),
        }


@dataclass(frozen=True, slots=True)
class StabilityDecompositionMetrics:
    total_folds: int
    failed_folds: int
    diagnosable_failed_folds: int
    explained_failed_folds: int
    unexplained_failed_folds: int
    failed_fold_driver_coverage: float | None
    primary_driver: InstabilityDriver | None
    driver_counts: tuple[tuple[InstabilityDriver, int], ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "driver_counts", tuple(self.driver_counts))

    def to_payload(self) -> dict[str, Any]:
        return {
            "total_folds": self.total_folds,
            "failed_folds": self.failed_folds,
            "diagnosable_failed_folds": self.diagnosable_failed_folds,
            "explained_failed_folds": self.explained_failed_folds,
            "unexplained_failed_folds": self.unexplained_failed_folds,
            "failed_fold_driver_coverage": self.failed_fold_driver_coverage,
            "primary_driver": self.primary_driver.value if self.primary_driver else None,
            "driver_counts": [{"driver": driver.value, "count": count} for driver, count in self.driver_counts],
        }


@dataclass(frozen=True, slots=True)
class StabilityDecompositionReport:
    source_bundle_sha256: str
    walk_forward_report_sha256: str
    walk_forward_status: WalkForwardStatus
    decomposition_policy: StabilityDecompositionPolicy
    folds: tuple[FoldDecomposition, ...]
    metrics: StabilityDecompositionMetrics
    status: DecompositionStatus
    reasons: tuple[str, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "folds", tuple(self.folds))
        object.__setattr__(self, "reasons", tuple(self.reasons))
        if self.metrics.total_folds != len(self.folds):
            raise ValueError("decomposition metrics fold count is inconsistent")

    def canonical_payload(self) -> dict[str, Any]:
        return {
            "schema": _DECOMPOSITION_SCHEMA,
            "source_bundle_sha256": self.source_bundle_sha256,
            "walk_forward_report_sha256": self.walk_forward_report_sha256,
            "walk_forward_status": self.walk_forward_status.value,
            "decomposition_policy": self.decomposition_policy.to_payload(),
            "folds": [fold.to_payload() for fold in self.folds],
            "metrics": self.metrics.to_payload(),
            "status": self.status.value,
            "reasons": list(self.reasons),
            "post_hoc_diagnostic_only": True,
            "never_selects_policy": True,
            "drivers_are_diagnostic_not_causal_proof": True,
            "advisory_only": True,
        }

    @property
    def sha256(self) -> str:
        return _sha256(self.canonical_payload())

    def to_envelope(self) -> dict[str, Any]:
        return {"payload": self.canonical_payload(), "sha256": self.sha256}


@dataclass(frozen=True, slots=True)
class _CaseDiagnostic:
    result: ReplayResult
    capacity_ratio: float
    quote_age_ms: int


def _subset_cases(bundle: ReplayBundle, operation_ids: Sequence[str]) -> tuple[ReplayCase, ...]:
    latest = {case.logical_operation_id: case for case in bundle.collapsed_cases()}
    missing = [operation_id for operation_id in operation_ids if operation_id not in latest]
    if missing:
        raise ValueError("decomposition subset is missing logical operations")
    return tuple(latest[operation_id] for operation_id in operation_ids)


def _diagnose_case(case: ReplayCase, candidate: JointPolicyCandidate) -> _CaseDiagnostic:
    engine_policy = replace(case.engine_policy, execute_net_edge=candidate.execute_net_edge_bps / 10_000.0)
    regime_policy = replace(case.regime_policy, volatile_return_bps=candidate.volatile_return_bps)
    result = replay_case(case, engine_policy=engine_policy, regime_policy=regime_policy)
    context = derive_window_regime_context(
        case.build_route(),
        case.snapshots,
        windows_by_market=case.windows_by_market,
        evaluation_time_ms=case.evaluation_time_ms,
        start_amount=case.start_amount,
        regime_policy=regime_policy,
    )
    if result.regime is not context.classification.regime:
        raise RuntimeError("replay regime diverged from route-bound diagnostic regime")
    features = context.classification.features
    return _CaseDiagnostic(result=result, capacity_ratio=features.top_of_book_capacity_ratio, quote_age_ms=features.quote_age_ms)


def _distribution_tv(left: Sequence[str], right: Sequence[str]) -> float:
    if not left or not right:
        raise ValueError("distribution shift requires non-empty populations")
    left_counts = Counter(left)
    right_counts = Counter(right)
    keys = set(left_counts) | set(right_counts)
    return 0.5 * sum(abs(left_counts[key] / len(left) - right_counts[key] / len(right)) for key in keys)


def _overprediction_penalty(results: Sequence[ReplayResult]) -> float | None:
    metrics = calculate_replay_metrics(results)
    if metrics.mean_prediction_error_bps is None:
        return None
    return max(0.0, -metrics.mean_prediction_error_bps)


def _support_rates(evaluation: Any, operations: int) -> tuple[float, float]:
    if operations <= 0:
        raise ValueError("causal-support rate requires operations")
    support = evaluation.causal_support
    return (support.execute_final_verdict_changes / operations, support.volatility_final_verdict_changes / operations)


def _selected_calibration_evaluation(fold: WalkForwardFold) -> Any:
    selected = fold.joint_report.selected_candidate
    if selected is None:
        return None
    for evaluation in fold.joint_report.calibration_evaluations:
        if evaluation.candidate == selected:
            return evaluation
    raise ValueError("selected policy has no calibration evaluation")


_DRIVER_ORDER = (
    InstabilityDriver.REGIME_DRIFT,
    InstabilityDriver.ROUTE_DRIFT,
    InstabilityDriver.LIQUIDITY_DETERIORATION,
    InstabilityDriver.FRESHNESS_DETERIORATION,
    InstabilityDriver.PREDICTION_BIAS_WORSENING,
    InstabilityDriver.CAUSAL_SUPPORT_LOSS,
)


def _driver_scores(metrics: FoldDriftMetrics, policy: StabilityDecompositionPolicy) -> dict[InstabilityDriver, float]:
    pairs = (
        (InstabilityDriver.REGIME_DRIFT, metrics.regime_tv_distance, policy.regime_tv_threshold),
        (InstabilityDriver.ROUTE_DRIFT, metrics.route_tv_distance, policy.route_tv_threshold),
        (InstabilityDriver.LIQUIDITY_DETERIORATION, metrics.capacity_ratio_drop_fraction, policy.capacity_ratio_drop_fraction_threshold),
        (InstabilityDriver.FRESHNESS_DETERIORATION, metrics.quote_age_increase_ms, policy.quote_age_increase_ms_threshold),
        (InstabilityDriver.CAUSAL_SUPPORT_LOSS, metrics.causal_support_rate_drop, policy.causal_support_rate_drop_threshold),
    )
    scores: dict[InstabilityDriver, float] = {}
    for driver, value, threshold in pairs:
        if value >= threshold:
            scores[driver] = value / threshold if threshold > 0 else (math.inf if value > 0 else 1.0)
    bias = metrics.overprediction_penalty_increase_bps
    if bias is not None and bias >= policy.overprediction_penalty_increase_bps_threshold:
        threshold = policy.overprediction_penalty_increase_bps_threshold
        scores[InstabilityDriver.PREDICTION_BIAS_WORSENING] = bias / threshold if threshold > 0 else (math.inf if bias > 0 else 1.0)
    return scores


def _primary_driver(scores: Mapping[InstabilityDriver, float]) -> InstabilityDriver | None:
    if not scores:
        return None
    order = {driver: index for index, driver in enumerate(_DRIVER_ORDER)}
    return sorted(scores, key=lambda driver: (-scores[driver], order[driver]))[0]


def _fold_decomposition(bundle: ReplayBundle, fold: WalkForwardFold, policy: StabilityDecompositionPolicy) -> FoldDecomposition:
    candidate = fold.selected_candidate
    if candidate is None:
        attributed = () if fold.passed else (InstabilityDriver.INSUFFICIENT_DIAGNOSTIC_EVIDENCE,)
        return FoldDecomposition(fold.plan.index, fold.passed, None, None, (), attributed, attributed[0] if attributed else None, ("fold selected no policy; drift diagnostics are unavailable",))
    calibration_cases = _subset_cases(bundle, fold.plan.calibration_operation_ids)
    validation_cases = _subset_cases(bundle, fold.plan.validation_operation_ids)
    if len(calibration_cases) < policy.min_operations_per_side or len(validation_cases) < policy.min_operations_per_side:
        attributed = () if fold.passed else (InstabilityDriver.INSUFFICIENT_DIAGNOSTIC_EVIDENCE,)
        return FoldDecomposition(fold.plan.index, fold.passed, candidate, None, (), attributed, attributed[0] if attributed else None, (_SPARSE_DIAGNOSTIC_REASON,))
    calibration = tuple(_diagnose_case(case, candidate) for case in calibration_cases)
    validation = tuple(_diagnose_case(case, candidate) for case in validation_cases)
    cal_results = tuple(item.result for item in calibration)
    val_results = tuple(item.result for item in validation)
    regime_tv = _distribution_tv([item.result.regime.value for item in calibration], [item.result.regime.value for item in validation])
    route_tv = _distribution_tv([item.result.route_id for item in calibration], [item.result.route_id for item in validation])
    cal_capacity = float(median(item.capacity_ratio for item in calibration))
    val_capacity = float(median(item.capacity_ratio for item in validation))
    capacity_drop = max(0.0, (cal_capacity - val_capacity) / cal_capacity)
    cal_age = float(median(item.quote_age_ms for item in calibration))
    val_age = float(median(item.quote_age_ms for item in validation))
    quote_age_increase = max(0.0, val_age - cal_age)
    cal_bias = _overprediction_penalty(cal_results)
    val_bias = _overprediction_penalty(val_results)
    bias_increase = None if cal_bias is None or val_bias is None else max(0.0, val_bias - cal_bias)
    cal_eval = _selected_calibration_evaluation(fold)
    val_eval = fold.joint_report.validation_evaluation
    if cal_eval is None or val_eval is None:
        raise ValueError("selected walk-forward fold lacks causal-support evaluations")
    cal_execute, cal_vol = _support_rates(cal_eval, len(calibration_cases))
    val_execute, val_vol = _support_rates(val_eval, len(validation_cases))
    support_drop = max(0.0, cal_execute - val_execute, cal_vol - val_vol)
    metrics = FoldDriftMetrics(
        len(calibration_cases), len(validation_cases), regime_tv, route_tv,
        cal_capacity, val_capacity, capacity_drop, cal_age, val_age, quote_age_increase,
        cal_bias, val_bias, bias_increase, cal_execute, val_execute, cal_vol, val_vol, support_drop,
    )
    scores = _driver_scores(metrics, policy)
    observed = tuple(driver for driver in _DRIVER_ORDER if driver in scores)
    if fold.passed:
        attributed = ()
        primary = None
        reasons = ("validation passed; drift triggers are diagnostic only",)
    elif observed:
        attributed = observed
        primary = _primary_driver(scores)
        reasons = ("failed validation has one or more threshold-crossing drift drivers",)
    else:
        attributed = (InstabilityDriver.UNEXPLAINED_FAILURE,)
        primary = InstabilityDriver.UNEXPLAINED_FAILURE
        reasons = ("failed validation did not cross configured decomposition thresholds",)
    return FoldDecomposition(fold.plan.index, fold.passed, candidate, metrics, observed, attributed, primary, reasons)


def _aggregate_metrics(folds: Sequence[FoldDecomposition]) -> StabilityDecompositionMetrics:
    failed = [fold for fold in folds if not fold.validation_passed]
    diagnosable = [fold for fold in failed if fold.metrics is not None]
    explained = [fold for fold in failed if any(driver in _DRIVER_ORDER for driver in fold.attributed_drivers)]
    unexplained = [fold for fold in failed if InstabilityDriver.UNEXPLAINED_FAILURE in fold.attributed_drivers]
    counts = Counter(driver for fold in failed for driver in fold.attributed_drivers if driver in _DRIVER_ORDER)
    ordered_counts = tuple((driver, counts[driver]) for driver in _DRIVER_ORDER if counts[driver] > 0)
    primary = None
    if ordered_counts:
        order = {driver: index for index, driver in enumerate(_DRIVER_ORDER)}
        primary = sorted(counts, key=lambda driver: (-counts[driver], order[driver]))[0]
    return StabilityDecompositionMetrics(
        len(folds), len(failed), len(diagnosable), len(explained), len(unexplained),
        len(explained) / len(failed) if failed else None, primary, ordered_counts,
    )


def run_stability_decomposition(bundle: ReplayBundle, walk_forward_report: WalkForwardReport, policy: StabilityDecompositionPolicy | None = None) -> StabilityDecompositionReport:
    active = policy or StabilityDecompositionPolicy()
    verify_walk_forward_report_bundle_binding(walk_forward_report, bundle)
    folds = tuple(_fold_decomposition(bundle, fold, active) for fold in walk_forward_report.folds)
    metrics = _aggregate_metrics(folds)
    if walk_forward_report.status is WalkForwardStatus.PASSED_STABILITY:
        status = DecompositionStatus.STABLE_BASELINE
        reasons = ("walk-forward baseline passed; decomposition is diagnostic only",)
    elif walk_forward_report.status in {WalkForwardStatus.INSUFFICIENT_CORPUS, WalkForwardStatus.INSUFFICIENT_FOLDS}:
        status = DecompositionStatus.INSUFFICIENT_EVIDENCE
        reasons = ("walk-forward evidence is insufficient for instability attribution",)
    elif metrics.failed_folds == 0:
        status = DecompositionStatus.INSUFFICIENT_EVIDENCE
        reasons = ("unstable walk-forward report has no failed folds to decompose",)
    elif metrics.explained_failed_folds == metrics.failed_folds:
        status = DecompositionStatus.DECOMPOSED_INSTABILITY
        reasons = ("all failed folds have threshold-crossing diagnostic drivers",)
    elif metrics.explained_failed_folds > 0:
        status = DecompositionStatus.PARTIALLY_DECOMPOSED
        reasons = ("some failed folds remain unexplained or lack diagnostic evidence",)
    elif metrics.diagnosable_failed_folds > 0:
        status = DecompositionStatus.UNEXPLAINED_INSTABILITY
        reasons = ("failed folds were diagnosable but no configured drift driver crossed its threshold",)
    else:
        status = DecompositionStatus.INSUFFICIENT_EVIDENCE
        reasons = ("failed folds lack selected-policy diagnostic evidence",)
    return StabilityDecompositionReport(bundle.sha256, walk_forward_report.sha256, walk_forward_report.status, active, folds, metrics, status, reasons)


def _expected_fold_drivers(metrics: Mapping[str, Any] | None, passed: bool, policy: StabilityDecompositionPolicy) -> tuple[list[str], list[str], str | None]:
    if metrics is None:
        attributed = [] if passed else [InstabilityDriver.INSUFFICIENT_DIAGNOSTIC_EVIDENCE.value]
        return [], attributed, attributed[0] if attributed else None
    typed = FoldDriftMetrics(**metrics)
    scores = _driver_scores(typed, policy)
    observed = [driver.value for driver in _DRIVER_ORDER if driver in scores]
    if passed:
        return observed, [], None
    if observed:
        primary = _primary_driver(scores)
        return observed, observed, primary.value if primary else None
    return [], [InstabilityDriver.UNEXPLAINED_FAILURE.value], InstabilityDriver.UNEXPLAINED_FAILURE.value


def verify_stability_decomposition_report_envelope(envelope: Mapping[str, Any]) -> dict[str, Any]:
    try:
        payload = envelope["payload"]
        supplied_sha = envelope["sha256"]
    except KeyError as exc:
        raise ValueError("stability decomposition envelope is incomplete") from exc
    if not isinstance(payload, dict) or not isinstance(supplied_sha, str):
        raise ValueError("stability decomposition envelope has invalid types")
    expected_keys = {"schema", "source_bundle_sha256", "walk_forward_report_sha256", "walk_forward_status", "decomposition_policy", "folds", "metrics", "status", "reasons", "post_hoc_diagnostic_only", "never_selects_policy", "drivers_are_diagnostic_not_causal_proof", "advisory_only"}
    if set(payload) != expected_keys:
        raise ValueError("stability decomposition payload fields are not canonical")
    if payload.get("schema") != _DECOMPOSITION_SCHEMA:
        raise ValueError("unsupported stability decomposition schema")
    if payload.get("walk_forward_status") not in {status.value for status in WalkForwardStatus}:
        raise ValueError("stability decomposition walk-forward status is invalid")
    if payload.get("status") not in {status.value for status in DecompositionStatus}:
        raise ValueError("stability decomposition status is invalid")
    for key in ("post_hoc_diagnostic_only", "never_selects_policy", "drivers_are_diagnostic_not_causal_proof", "advisory_only"):
        if payload.get(key) is not True:
            raise ValueError(f"stability decomposition invariant flag is invalid: {key}")
    if not isinstance(payload.get("decomposition_policy"), dict):
        raise ValueError("stability decomposition policy must be an object")
    policy = StabilityDecompositionPolicy(**payload["decomposition_policy"])
    folds = payload.get("folds")
    if not isinstance(folds, list):
        raise ValueError("stability decomposition folds must be a list")
    for expected_index, fold in enumerate(folds, start=1):
        if not isinstance(fold, dict):
            raise ValueError("stability decomposition fold must be an object")
        expected_fold_keys = {"fold_index", "validation_passed", "selected_candidate", "metrics", "observed_drivers", "attributed_drivers", "primary_driver", "reasons"}
        if set(fold) != expected_fold_keys or fold["fold_index"] != expected_index:
            raise ValueError("stability decomposition fold fields are not canonical")
        selected = fold["selected_candidate"]
        if selected is not None and not isinstance(selected, dict):
            raise ValueError("stability decomposition selected candidate must be an object or null")
        if fold["metrics"] is None and selected is not None and fold["reasons"] != [_SPARSE_DIAGNOSTIC_REASON]:
            raise ValueError("selected fold without metrics lacks explicit sparse diagnostic evidence")
        observed, attributed, primary = _expected_fold_drivers(fold["metrics"], bool(fold["validation_passed"]), policy)
        if fold["observed_drivers"] != observed:
            raise ValueError("stability decomposition observed drivers do not match metrics")
        if fold["attributed_drivers"] != attributed:
            raise ValueError("stability decomposition attributed drivers do not match metrics")
        if fold["primary_driver"] != primary:
            raise ValueError("stability decomposition primary driver does not match metrics")
    driver_values = {item.value for item in _DRIVER_ORDER}
    failed = [fold for fold in folds if not fold["validation_passed"]]
    diagnosable = [fold for fold in failed if fold["metrics"] is not None]
    explained = [fold for fold in failed if any(driver in driver_values for driver in fold["attributed_drivers"])]
    unexplained = [fold for fold in failed if InstabilityDriver.UNEXPLAINED_FAILURE.value in fold["attributed_drivers"]]
    counts = Counter(driver for fold in failed for driver in fold["attributed_drivers"] if driver in driver_values)
    expected_counts = [{"driver": driver.value, "count": counts[driver.value]} for driver in _DRIVER_ORDER if counts[driver.value] > 0]
    primary_driver = None
    if expected_counts:
        primary_driver = sorted(expected_counts, key=lambda item: (-item["count"], [d.value for d in _DRIVER_ORDER].index(item["driver"])))[0]["driver"]
    expected_metrics = {
        "total_folds": len(folds),
        "failed_folds": len(failed),
        "diagnosable_failed_folds": len(diagnosable),
        "explained_failed_folds": len(explained),
        "unexplained_failed_folds": len(unexplained),
        "failed_fold_driver_coverage": len(explained) / len(failed) if failed else None,
        "primary_driver": primary_driver,
        "driver_counts": expected_counts,
    }
    if payload.get("metrics") != expected_metrics:
        raise ValueError("stability decomposition aggregate metrics do not match fold evidence")
    digest = _sha256(payload)
    if not hmac.compare_digest(digest, supplied_sha):
        raise ValueError("stability decomposition SHA-256 does not match payload")
    _canonical_json(payload)
    return dict(payload)


def verify_stability_decomposition_bundle_binding(report: StabilityDecompositionReport, walk_forward_report: WalkForwardReport, bundle: ReplayBundle) -> bool:
    if report.source_bundle_sha256 != bundle.sha256:
        raise ValueError("stability decomposition source bundle SHA-256 does not match bundle")
    if report.walk_forward_report_sha256 != walk_forward_report.sha256:
        raise ValueError("stability decomposition walk-forward SHA-256 does not match report")
    rebuilt = run_stability_decomposition(bundle, walk_forward_report, report.decomposition_policy)
    if rebuilt.canonical_payload() != report.canonical_payload():
        raise ValueError("stability decomposition does not reproduce from evidence")
    return True
