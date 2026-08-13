import pytest

from resonance_arbitrage_graph.engine import evaluate_route
from resonance_arbitrage_graph.quotes import CostAssumption, QuoteSnapshot, quote_to_trade_edges
from resonance_arbitrage_graph.regime import MarketRegime
from resonance_arbitrage_graph.rolling_state import RollingMarketWindow, RollingWindowPolicy
from resonance_arbitrage_graph.window_regime import derive_window_regime_context, market_key


_ZERO_COST = CostAssumption(fee_bps=0.0, slippage_bps=0.0)


def _quote(symbol: str, base: str, quote: str, ts: int, mid: float) -> QuoteSnapshot:
    return QuoteSnapshot(
        venue="binance",
        symbol=symbol,
        base_asset=base,
        quote_asset=quote,
        bid_price=mid - 0.05,
        bid_qty=100.0,
        ask_price=mid + 0.05,
        ask_qty=100.0,
        observed_at_ms=ts,
        source_url=f"fixture:{symbol}",
    )


def _window(symbol: str, base: str, quote: str, mids: list[float]) -> RollingMarketWindow:
    quotes = [
        _quote(symbol, base, quote, ts, mid)
        for ts, mid in zip((0, 15_000, 30_000, 45_000, 60_000), mids)
    ]
    return RollingMarketWindow.from_quotes(
        quotes,
        policy=RollingWindowPolicy(horizon_ms=60_000, min_samples=5, min_coverage_ratio=1.0),
        end_ms=60_000,
    )


def _route():
    btc_usdt = _quote("BTCUSDT", "BTC", "USDT", 60_000, 100.0)
    eth_btc = _quote("ETHBTC", "ETH", "BTC", 60_000, 0.5)
    eth_usdt = _quote("ETHUSDT", "ETH", "USDT", 60_000, 50.0)
    btc_buy, _ = quote_to_trade_edges(btc_usdt, _ZERO_COST, now_ms=60_000)
    eth_buy, _ = quote_to_trade_edges(eth_btc, _ZERO_COST, now_ms=60_000)
    _, eth_sell = quote_to_trade_edges(eth_usdt, _ZERO_COST, now_ms=60_000)
    edges = (btc_buy, eth_buy, eth_sell)
    snapshots = (btc_usdt, eth_btc, eth_usdt)
    return edges, snapshots, evaluate_route(edges, 100.0)


def test_complete_windows_drive_regime_without_caller_volatility():
    edges, snapshots, result = _route()
    windows = {
        market_key("binance", "BTCUSDT"): _window("BTCUSDT", "BTC", "USDT", [100, 100.1, 99.9, 100.2, 100.0]),
        market_key("binance", "ETHBTC"): _window("ETHBTC", "ETH", "BTC", [0.5, 0.501, 0.499, 0.502, 0.5]),
        market_key("binance", "ETHUSDT"): _window("ETHUSDT", "ETH", "USDT", [50, 50.1, 49.9, 50.2, 50.0]),
    }

    context = derive_window_regime_context(
        edges,
        snapshots,
        windows_by_market=windows,
        evaluation_time_ms=60_000,
        start_amount=result.start_amount,
    )

    assert context.classification.features.short_window_return_volatility_bps is not None
    assert context.classification.regime is not MarketRegime.UNKNOWN
    assert len(context.window_sha256_by_market) == 3


def test_missing_window_fails_closed():
    edges, snapshots, result = _route()
    with pytest.raises(ValueError, match="missing rolling window"):
        derive_window_regime_context(
            edges,
            snapshots,
            windows_by_market={},
            evaluation_time_ms=60_000,
            start_amount=result.start_amount,
        )


def test_incomplete_window_yields_unknown():
    edges, snapshots, result = _route()
    complete = _window("BTCUSDT", "BTC", "USDT", [100, 100.1, 99.9, 100.2, 100.0])
    incomplete = RollingMarketWindow.from_quotes(
        [_quote("ETHBTC", "ETH", "BTC", 50_000, 0.5), _quote("ETHBTC", "ETH", "BTC", 60_000, 0.501)],
        policy=RollingWindowPolicy(horizon_ms=60_000, min_samples=5, min_coverage_ratio=0.8),
        end_ms=60_000,
    )
    windows = {
        market_key("binance", "BTCUSDT"): complete,
        market_key("binance", "ETHBTC"): incomplete,
        market_key("binance", "ETHUSDT"): _window("ETHUSDT", "ETH", "USDT", [50, 50.1, 49.9, 50.2, 50.0]),
    }

    context = derive_window_regime_context(
        edges,
        snapshots,
        windows_by_market=windows,
        evaluation_time_ms=60_000,
        start_amount=result.start_amount,
    )

    assert context.classification.regime is MarketRegime.UNKNOWN
    assert "rolling_window_incomplete" in context.classification.reasons
