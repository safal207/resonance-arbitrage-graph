from __future__ import annotations

import hashlib

import pytest

pytest.importorskip("catboost")

from resonance_arbitrage_graph.predictive import (
    OpportunityFeatureVector,
    PredictiveDataset,
    PredictiveRow,
    PredictiveTargetLabels,
    verify_predictive_receipt_binding,
)
from resonance_arbitrage_graph.predictive_catboost import (
    CatBoostResearchConfig,
    encode_feature_vector,
    fit_catboost_predictive_model,
    predict_with_catboost,
    run_catboost_walk_forward,
)


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _vector(index: int) -> OpportunityFeatureVector:
    decision = (index + 1) * 100
    return OpportunityFeatureVector(
        logical_operation_id=f"op-{index}",
        decision_at_ms=decision,
        route_id=_sha(f"route-{index % 3}"),
        start_amount=1_000.0,
        deterministic_verdict="EXECUTE_SIM" if index % 4 != 2 else "OBSERVE",
        market_regime=("NORMAL", "VOLATILE", "THIN_LIQUIDITY")[index % 3],
        expected_edge_bps=float(5 + index),
        required_edge_bps=0.0,
        route_hops=3,
        total_cost_bps=float(index % 3),
        total_latency_ms=100 + index,
        route_success_probability=max(0.50, 0.99 - index * 0.02),
        normalized_spread_bps=2.0 + index * 0.1,
        top_of_book_capacity_ratio=2.0 + index * 0.05,
        quote_age_ms=10 + index,
        quote_age_dispersion_ms=index,
        cross_rate_dislocation_bps=float(index),
        short_window_return_volatility_bps=5.0 + index,
        min_window_sample_count=5,
        min_window_coverage_ratio=1.0,
        venue_sequence=("fixture", "fixture", "fixture"),
        symbol_sequence=("BTCUSDT", "ETHBTC", "ETHUSDT"),
        side_sequence=("BUY", "BUY", "SELL"),
        asset_path=("USDT", "BTC", "ETH", "USDT"),
        same_venue=True,
        policy_context_sha256=_sha("policy"),
        source_replay_case_sha256=_sha(f"case-{index}"),
    )


def _row(
    index: int,
    edge_bps: float | None,
    *,
    expired: bool = False,
    late_target: bool = False,
) -> PredictiveRow:
    vector = _vector(index)
    available_at = 9_999 if late_target else vector.decision_at_ms + 10
    if expired:
        targets = PredictiveTargetLabels(
            target_available_at_ms=available_at,
            future_net_edge_bps=None,
            survived=False,
            positive_realized_pnl=False,
            met_required_edge=False,
            realized_paper_pnl_units=None,
        )
    else:
        assert edge_bps is not None
        pnl = 1_000.0 * edge_bps / 10_000.0
        targets = PredictiveTargetLabels(
            target_available_at_ms=available_at,
            future_net_edge_bps=edge_bps,
            survived=True,
            positive_realized_pnl=pnl > 0.0,
            met_required_edge=edge_bps >= 0.0,
            realized_paper_pnl_units=pnl,
        )
    return PredictiveRow(feature_vector=vector, targets=targets)


def _dataset() -> PredictiveDataset:
    rows = (
        _row(0, 10.0, late_target=True),
        _row(1, -5.0),
        _row(2, None, expired=True),
        _row(3, 20.0),
        _row(4, -10.0),
        _row(5, 5.0),
        _row(6, 15.0),
        _row(7, -3.0),
        _row(8, 8.0),
    )
    return PredictiveDataset(source_bundle_sha256=_sha("bundle"), rows=rows)


def _config() -> CatBoostResearchConfig:
    return CatBoostResearchConfig(
        iterations=12,
        depth=3,
        learning_rate=0.1,
        l2_leaf_reg=2.0,
        random_seed=7,
        thread_count=1,
    )


def _training_rows() -> tuple[PredictiveRow, ...]:
    dataset = _dataset()
    return tuple(
        row
        for row in dataset.rows[:6]
        if row.targets.target_available_at_ms is not None
        and row.targets.target_available_at_ms <= dataset.rows[6].decision_at_ms
    )


def test_catboost_encoder_is_feature_only_and_shape_stable():
    vector = _vector(1)
    encoded = encode_feature_vector(vector)

    assert len(encoded) == 25
    assert "op-1" not in encoded
    assert vector.source_replay_case_sha256 not in encoded
    assert encoded[-6] == vector.market_regime


def test_catboost_model_binds_artifact_and_prediction_receipts():
    dataset = _dataset()
    model = fit_catboost_predictive_model(_training_rows(), config=_config())
    prediction = predict_with_catboost(model, (dataset.rows[6],))[0]

    assert model.model_id.startswith("pmo_")
    assert len(prediction.receipts) == 3
    assert 0.0 <= prediction.survival_probability <= 1.0
    assert 0.0 <= prediction.positive_realized_pnl_probability <= 1.0
    assert model.artifact.parameters["regressor_sha256"]
    assert model.artifact.parameters["catboost_version"]

    for receipt in prediction.receipts:
        verify_predictive_receipt_binding(receipt, dataset.rows[6], model)


def test_catboost_model_identity_is_deterministic_for_same_training_context():
    training = _training_rows()
    first = fit_catboost_predictive_model(training, config=_config())
    second = fit_catboost_predictive_model(training, config=_config())

    assert first.manifest.sha256 == second.manifest.sha256
    assert first.artifact.sha256 == second.artifact.sha256
    assert first.model_id == second.model_id
    assert first.artifact.parameters["regressor_sha256"] == second.artifact.parameters["regressor_sha256"]
    assert first.artifact.parameters["survival_head"] == second.artifact.parameters["survival_head"]
    assert first.artifact.parameters["positive_pnl_head"] == second.artifact.parameters["positive_pnl_head"]


def test_walk_forward_compares_same_rows_and_exposes_late_target_exclusion():
    comparison = run_catboost_walk_forward(
        _dataset(),
        config=_config(),
        min_training_rows=4,
    )

    assert comparison.successful_fold_count >= 1
    assert comparison.historical_mean.evaluated_rows == comparison.catboost.evaluated_rows
    assert comparison.historical_mean.evaluated_rows == comparison.successful_fold_count
    assert "op-0" in comparison.excluded_late_target_operation_ids
    assert comparison.paper_only is True
    assert len(comparison.sha256) == 64


def test_catboost_training_rejects_unavailable_targets():
    unavailable = PredictiveRow(
        feature_vector=_vector(9),
        targets=PredictiveTargetLabels(
            target_available_at_ms=None,
            future_net_edge_bps=None,
            survived=None,
            positive_realized_pnl=None,
            met_required_edge=None,
            realized_paper_pnl_units=None,
        ),
    )
    with pytest.raises(ValueError, match="available targets"):
        fit_catboost_predictive_model((_row(1, 1.0), unavailable), config=_config())
