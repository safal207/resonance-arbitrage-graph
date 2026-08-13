import pytest

from resonance_arbitrage_graph.quotes import CostAssumption, QuoteSnapshot, quote_to_trade_edges
from resonance_arbitrage_graph.regime_features import derive_route_regime_features


_ZERO_COST = CostAssumption(fee_bps=0.0, slippage_bps=0.0)


def _quote(
    symbol: str,
    base: str,
    quote: str,
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
        base_asset=base,
        quote_asset=quote,
        bid_price=bid,
        bid_qty=bid_qty,
        ask_price=ask,
        ask_qty=ask_qty,
        observed_at_ms=observed_at_ms,
        source_url=f"fixture:{symbol}",
    )


def _triangle(evaluation_time_ms: int = 10_000):
    btc_usdt = _quote(
        "BTCUSDT",
        "BTC",
        "USDT",
        bid=100.0,
        ask=100.1,
        bid_qty=5.0,
        ask_qty=4.0,
        observed_at_ms=9_900,
    )
    eth_btc = _quote(
        "ETHBTC",
        "ETH",
        "BTC",
        bid=0.49,
        ask=0.5,
        bid_qty=12.0,
        ask_qty=10.0,
        observed_at_ms=9_800,
    )
    eth_usdt = _quote(
        "ETHUSDT",
        "ETH",
        "USDT",
        bid=50.0,
        ask=50.2,
        bid_qty=15.0,
        ask_qty=15.0,
        observed_at_ms=9_500,
    )

    btc_buy, _ = quote_to_trade_edges(btc_usdt, _ZERO_COST, now_ms=evaluation_time_ms)
    eth_buy, _ = quote_to_trade_edges(eth_btc, _ZERO_COST, now_ms=evaluation_time_ms)
    _, eth_sell = quote_to_trade_edges(eth_usdt, _ZERO_COST, now_ms=evaluation_time_ms)
    return (btc_buy, eth_buy, eth_sell), (btc_usdt, eth_btc, eth_usdt)


def test_route_features_use_bound_spreads_leg_capacity_and_freshness():
    edges, snapshots = _triangle()
    features = derive_route_regime_features(
        edges,
        snapshots,
        evaluation_time_ms=10_000,
        start_amount=100.0,
        cross_rate_dislocation_bps=12.0,
        short_window_return_volatility_bps=30.0,
    )

    assert features.normalized_spread_bps > 30.0
    assert features.top_of_book_capacity_ratio == pytest.approx(4.004)
    assert features.quote_age_ms == 500
    assert features.quote_age_dispersion_ms == 400
    assert features.cross_rate_dislocation_bps == 12.0
    assert features.short_window_return_volatility_bps == 30.0


def test_feature_derivation_rejects_future_snapshot_and_invalid_start_amount():
    edges, snapshots = _triangle(evaluation_time_ms=10_002)
    future = _quote(
        "BTCUSDT",
        "BTC",
        "USDT",
        bid=100.0,
        ask=100.1,
        bid_qty=5.0,
        ask_qty=4.0,
        observed_at_ms=10_003,
    )
    future_buy, _ = quote_to_trade_edges(future, _ZERO_COST, now_ms=10_002)

    with pytest.raises(ValueError, match="future"):
        derive_route_regime_features(
            [future_buy],
            [future],
            evaluation_time_ms=10_002,
            start_amount=100.0,
        )

    with pytest.raises(ValueError, match="start_amount"):
        derive_route_regime_features(
            edges,
            snapshots,
            evaluation_time_ms=10_002,
            start_amount=0.0,
        )
