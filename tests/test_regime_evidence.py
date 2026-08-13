from dataclasses import replace

import pytest

from resonance_arbitrage_graph.engine import evaluate_route
from resonance_arbitrage_graph.quotes import CostAssumption, QuoteSnapshot, quote_to_trade_edges
from resonance_arbitrage_graph.regime import RegimeFeatures, classify_market_regime
from resonance_arbitrage_graph.regime_evidence import make_regime_market_evidence_receipt
from resonance_arbitrage_graph.regime_features import derive_route_regime_features


_ZERO_COST = CostAssumption(fee_bps=0.0, slippage_bps=0.0)


def _fixture():
    quote = QuoteSnapshot(
        venue="binance",
        symbol="BTCUSDT",
        base_asset="BTC",
        quote_asset="USDT",
        bid_price=100.0,
        bid_qty=5.0,
        ask_price=100.1,
        ask_qty=4.0,
        observed_at_ms=9_900,
        source_url="fixture:BTCUSDT",
    )
    buy, sell = quote_to_trade_edges(quote, _ZERO_COST, now_ms=10_000)
    route = (buy, sell)
    result = evaluate_route(route, 100.0)
    features = derive_route_regime_features(
        route,
        [quote],
        evaluation_time_ms=10_000,
        start_amount=100.0,
        short_window_return_volatility_bps=20.0,
    )
    classification = classify_market_regime(features)
    return quote, route, result, classification


def test_regime_receipt_binds_features_reasons_and_policy():
    quote, route, result, classification = _fixture()
    receipt = make_regime_market_evidence_receipt(
        "op-regime",
        route,
        result,
        snapshots=[quote],
        evaluation_time_ms=10_000,
        classification=classification,
    )

    regime = receipt.payload["market_regime"]
    assert regime["regime"] == classification.regime.value
    assert regime["features"] == classification.features.to_context()
    assert regime["reasons"] == list(classification.reasons)
    assert regime["policy"]["volatile_return_bps"] == 75.0
    assert len(receipt.sha256) == 64


def test_regime_receipt_rejects_feature_tampering():
    quote, route, result, classification = _fixture()
    tampered_features = replace(
        classification.features,
        normalized_spread_bps=classification.features.normalized_spread_bps + 1.0,
    )
    tampered = replace(classification, features=tampered_features)

    with pytest.raises(ValueError, match="features do not match"):
        make_regime_market_evidence_receipt(
            "op-regime",
            route,
            result,
            snapshots=[quote],
            evaluation_time_ms=10_000,
            classification=tampered,
        )


def test_regime_receipt_rejects_classification_tampering():
    quote, route, result, classification = _fixture()
    wrong_features = RegimeFeatures(
        normalized_spread_bps=classification.features.normalized_spread_bps,
        top_of_book_capacity_ratio=classification.features.top_of_book_capacity_ratio,
        quote_age_ms=classification.features.quote_age_ms,
        quote_age_dispersion_ms=classification.features.quote_age_dispersion_ms,
        cross_rate_dislocation_bps=100.0,
        short_window_return_volatility_bps=20.0,
    )
    wrong = replace(classification, features=wrong_features)

    with pytest.raises(ValueError, match="features do not match"):
        make_regime_market_evidence_receipt(
            "op-regime",
            route,
            result,
            snapshots=[quote],
            evaluation_time_ms=10_000,
            classification=wrong,
        )
