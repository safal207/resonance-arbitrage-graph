from copy import deepcopy
import hashlib
import json

import pytest

from resonance_arbitrage_graph.stability_decomposition import (
    DecompositionStatus,
    FoldDriftMetrics,
    InstabilityDriver,
    StabilityDecompositionPolicy,
    _driver_scores,
    run_stability_decomposition,
    verify_stability_decomposition_bundle_binding,
    verify_stability_decomposition_report_envelope,
)
from resonance_arbitrage_graph.walk_forward import run_walk_forward_stability
from test_walk_forward import _bundle, _grid, _policy


def _canonical_sha(payload: dict) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _metrics(**overrides) -> FoldDriftMetrics:
    values = dict(
        calibration_operations=10,
        validation_operations=5,
        regime_tv_distance=0.0,
        route_tv_distance=0.0,
        calibration_median_capacity_ratio=10.0,
        validation_median_capacity_ratio=10.0,
        capacity_ratio_drop_fraction=0.0,
        calibration_median_quote_age_ms=10.0,
        validation_median_quote_age_ms=10.0,
        quote_age_increase_ms=0.0,
        calibration_overprediction_penalty_bps=0.0,
        validation_overprediction_penalty_bps=0.0,
        overprediction_penalty_increase_bps=0.0,
        calibration_execute_support_rate=0.5,
        validation_execute_support_rate=0.5,
        calibration_volatility_support_rate=0.5,
        validation_volatility_support_rate=0.5,
        causal_support_rate_drop=0.0,
    )
    values.update(overrides)
    return FoldDriftMetrics(**values)


def test_driver_thresholds_cover_each_decomposition_dimension():
    policy = StabilityDecompositionPolicy(
        regime_tv_threshold=0.2,
        route_tv_threshold=0.2,
        capacity_ratio_drop_fraction_threshold=0.2,
        quote_age_increase_ms_threshold=100.0,
        overprediction_penalty_increase_bps_threshold=5.0,
        causal_support_rate_drop_threshold=0.2,
    )
    metrics = _metrics(
        regime_tv_distance=0.3,
        route_tv_distance=0.4,
        capacity_ratio_drop_fraction=0.3,
        quote_age_increase_ms=200.0,
        overprediction_penalty_increase_bps=8.0,
        causal_support_rate_drop=0.3,
    )

    assert set(_driver_scores(metrics, policy)) == {
        InstabilityDriver.REGIME_DRIFT,
        InstabilityDriver.ROUTE_DRIFT,
        InstabilityDriver.LIQUIDITY_DETERIORATION,
        InstabilityDriver.FRESHNESS_DETERIORATION,
        InstabilityDriver.PREDICTION_BIAS_WORSENING,
        InstabilityDriver.CAUSAL_SUPPORT_LOSS,
    }


def test_stable_walk_forward_remains_diagnostic_only():
    bundle = _bundle()
    walk = run_walk_forward_stability(bundle, _grid(), _policy())
    report = run_stability_decomposition(bundle, walk)

    assert report.status is DecompositionStatus.STABLE_BASELINE
    assert report.metrics.failed_folds == 0
    assert all(not fold.attributed_drivers for fold in report.folds)
    assert verify_stability_decomposition_bundle_binding(report, walk, bundle) is True


def test_failed_truth_fold_is_attributed_to_prediction_bias_when_other_thresholds_are_disabled():
    bundle = _bundle(bad_validation_truth=True)
    walk = run_walk_forward_stability(bundle, _grid(), _policy(min_pass_rate=1.0))
    report = run_stability_decomposition(
        bundle,
        walk,
        StabilityDecompositionPolicy(
            regime_tv_threshold=1.0,
            route_tv_threshold=1.0,
            capacity_ratio_drop_fraction_threshold=1.0,
            quote_age_increase_ms_threshold=1_000_000.0,
            overprediction_penalty_increase_bps_threshold=1.0,
            causal_support_rate_drop_threshold=1.0,
        ),
    )

    failed = [fold for fold in report.folds if not fold.validation_passed]
    assert failed
    assert any(InstabilityDriver.PREDICTION_BIAS_WORSENING in fold.attributed_drivers for fold in failed)
    assert report.status in {DecompositionStatus.DECOMPOSED_INSTABILITY, DecompositionStatus.PARTIALLY_DECOMPOSED}


def test_sparse_selected_policy_is_preserved_as_insufficient_diagnostic_evidence():
    bundle = _bundle(bad_validation_truth=True)
    walk = run_walk_forward_stability(bundle, _grid(), _policy(min_pass_rate=1.0))
    report = run_stability_decomposition(
        bundle,
        walk,
        StabilityDecompositionPolicy(min_operations_per_side=10),
    )

    sparse = [fold for fold in report.folds if fold.selected_candidate is not None and fold.metrics is None]
    assert sparse
    assert any(not fold.validation_passed for fold in sparse)
    for fold in sparse:
        assert fold.reasons == ("fold population is below decomposition minimum",)
        assert fold.observed_drivers == ()
        if fold.validation_passed:
            assert fold.attributed_drivers == ()
            assert fold.primary_driver is None
        else:
            assert fold.attributed_drivers == (InstabilityDriver.INSUFFICIENT_DIAGNOSTIC_EVIDENCE,)
            assert fold.primary_driver is InstabilityDriver.INSUFFICIENT_DIAGNOSTIC_EVIDENCE

    assert report.metrics.failed_folds == walk.metrics.failed_folds
    assert report.metrics.diagnosable_failed_folds == 0
    assert report.status is DecompositionStatus.INSUFFICIENT_EVIDENCE
    assert verify_stability_decomposition_bundle_binding(report, walk, bundle) is True


def test_sparse_selected_policy_reason_tamper_is_rejected_even_with_recomputed_sha():
    bundle = _bundle(bad_validation_truth=True)
    walk = run_walk_forward_stability(bundle, _grid(), _policy(min_pass_rate=1.0))
    report = run_stability_decomposition(
        bundle,
        walk,
        StabilityDecompositionPolicy(min_operations_per_side=10),
    )
    envelope = deepcopy(report.to_envelope())
    sparse = next(
        fold
        for fold in envelope["payload"]["folds"]
        if fold["selected_candidate"] is not None and fold["metrics"] is None
    )
    sparse["reasons"] = ["forged sparse evidence"]
    envelope["sha256"] = _canonical_sha(envelope["payload"])

    with pytest.raises(ValueError, match="explicit sparse diagnostic evidence"):
        verify_stability_decomposition_report_envelope(envelope)


def test_semantic_driver_tamper_is_rejected_even_with_recomputed_outer_sha():
    bundle = _bundle()
    walk = run_walk_forward_stability(bundle, _grid(), _policy())
    report = run_stability_decomposition(bundle, walk)
    envelope = deepcopy(report.to_envelope())
    envelope["payload"]["folds"][0]["observed_drivers"] = [InstabilityDriver.ROUTE_DRIFT.value]
    envelope["sha256"] = _canonical_sha(envelope["payload"])

    with pytest.raises(ValueError, match="observed drivers"):
        verify_stability_decomposition_report_envelope(envelope)


def test_decomposition_is_deterministic():
    bundle = _bundle(bad_validation_truth=True)
    walk = run_walk_forward_stability(bundle, _grid(), _policy(min_pass_rate=1.0))
    policy = StabilityDecompositionPolicy(overprediction_penalty_increase_bps_threshold=1.0)
    first = run_stability_decomposition(bundle, walk, policy)
    second = run_stability_decomposition(bundle, walk, policy)

    assert first.sha256 == second.sha256
    assert first.canonical_payload() == second.canonical_payload()
    assert verify_stability_decomposition_report_envelope(first.to_envelope()) == first.canonical_payload()
