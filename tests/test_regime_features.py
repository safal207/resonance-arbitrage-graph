import pytest

from resonance_arbitrage_graph.quotes import QuoteSnapshot
from resonance_arbitrage_graph.regime_features import derive_regime_features


def _quote(
    symbol: str,
    *,
    bid: float,
    ask: float,
    bid_qty: float,
    ask_qty: float,
    observed_at_ms: int,
) -> QuoteSnapshot:
    return QuoteSnapshot(
        venue="binance",
        symbol=symbol,
        base_asset="BTC",
        quote_asset="USDT",
        bid=bid,
        ask=ask,
        bid_qty=bid_qty,
        ask_qty=ask_qty,
        observed_at_ms=observed_at_ms,
        source_timestamp_ms=None,
        source_ref=f"fixture:{symbol}",
    )


def test_regime_features_use_worst_spread_capacity_and_quote_age():
    features = derive_regime_features(
        [
            _quote(
                "BTCUSDT",
                bid=100.0,
                ask=100.1,
                bid_qty=5.0,
                ask_qty=4.0,
                observed_at_ms=9_900,
            ),
            _quote(
                "ETHUSDT",
                bid=50.0,
                ask=50.2,
                bid_qty=2.0,
                ask_qty=3.0,
                observed_at_ms=9_500,
            ),
        ],
        evaluation_time_ms=10_000,
        reference_amount=1.0,
        cross_rate_dislocation_bps=12.0,
        short_window_return_volatility_bps=30.0,
    )

    assert features.normalized_spread_bps > 30.0
    assert features.top_of_book_capacity_ratio == pytest.approx(2.0)
    assert features.quote_age_ms == 500
    assert features.quote_age_dispersion_ms == 400
    assert features.cross_rate_dislocation_bps == 12.0
    assert features.short_window_return_volatility_bps == 30.0


def test_feature_derivation_rejects_future_quote_and_invalid_reference_amount():
    quote = _quote(
        "BTCUSDT",
        bid=100.0,
        ask=100.1,
        bid_qty=5.0,
        ask_qty=4.0,
        observed_at_ms=10_001,
    )
    with pytest.raises(ValueError, match="future"):
        derive_regime_features(
            [quote],
            evaluation_time_ms=10_000,
            reference_amount=1.0,
        )

    with pytest.raises(ValueError, match="reference_amount"):
        derive_regime_features(
            [quote],
            evaluation_time_ms=10_002,
            reference_amount=0.0,
        )
