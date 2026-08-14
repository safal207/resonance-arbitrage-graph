from __future__ import annotations

from dataclasses import replace
import hashlib

import pytest

from resonance_arbitrage_graph.predictive import (
    HistoricalMeanBaseline,
    OpportunityFeatureVector,
    PredictivePrediction,
    PredictiveRow,
    PredictiveTargetLabels,
    predict_with_historical_baseline,
)
from resonance_arbitrage_graph.predictive_verification import (
    verify_predictive_prediction_binding,
)


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _row(index: int, edge_bps: float | None) -> PredictiveRow:
    decision = (index + 1) * 100
    vector = OpportunityFeatureVector(
        logical_operation_id=f"op-{index}",
        decision_at_ms=decision,
        route_id=_sha("route"),
        start_amount=1_000.0,
        deterministic_verdict="EXECUTE_SIM",
        market_regime="NORMAL",
        expected_edge_bps=10.0,
        required_edge_bps=0.0,
        route_hops=3,
        total_cost_bps=1.0,
        total_latency_ms=100,
        route_success_probability=0.99,
        normalized_spread_bps=2.0,
        top_of_book_capacity_ratio=2.0,
        quote_age_ms=10,
        quote_age_dispersion_ms=1,
        cross_rate_dislocation_bps=1.0,
        short_window_return_volatility_bps=5.0,
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
    if edge_bps is None:
        targets = PredictiveTargetLabels(
            target_available_at_ms=None,
            future_net_edge_bps=None,
            survived=None,
            positive_realized_pnl=None,
            met_required_edge=None,
            realized_paper_pnl_units=None,
        )
    else:
        pnl = 1_000.0 * edge_bps / 10_000.0
        targets = PredictiveTargetLabels(
            target_available_at_ms=decision + 10,
            future_net_edge_bps=edge_bps,
            survived=True,
            positive_realized_pnl=pnl > 0.0,
            met_required_edge=edge_bps >= 0.0,
            realized_paper_pnl_units=pnl,
        )
    return PredictiveRow(feature_vector=vector, targets=targets)


def test_full_prediction_binding_accepts_consistent_receipts():
    model = HistoricalMeanBaseline.fit((_row(0, 10.0), _row(1, -5.0)))
    row = _row(2, None)
    prediction = predict_with_historical_baseline(model, (row,))[0]

    verify_predictive_prediction_binding(prediction, row, model)


def test_full_prediction_binding_rejects_receipt_value_drift():
    model = HistoricalMeanBaseline.fit((_row(0, 10.0), _row(1, -5.0)))
    row = _row(2, None)
    prediction = predict_with_historical_baseline(model, (row,))[0]

    tampered_receipt = replace(
        prediction.receipts[0],
        prediction_value=prediction.receipts[0].prediction_value + 1.0,
    )
    tampered = PredictivePrediction(
        logical_operation_id=prediction.logical_operation_id,
        model_id=prediction.model_id,
        predicted_future_net_edge_bps=prediction.predicted_future_net_edge_bps,
        survival_probability=prediction.survival_probability,
        positive_realized_pnl_probability=prediction.positive_realized_pnl_probability,
        receipts=(tampered_receipt, *prediction.receipts[1:]),
    )

    with pytest.raises(ValueError, match="receipt prediction value"):
        verify_predictive_prediction_binding(tampered, row, model)
