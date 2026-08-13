from dataclasses import replace

from resonance_arbitrage_graph.engine import evaluate_route
from resonance_arbitrage_graph.observation import verify_evidence_receipt
from resonance_arbitrage_graph.quotes import CostAssumption, QuoteSnapshot, quote_to_trade_edges
from resonance_arbitrage_graph.rolling_state import RollingMarketWindow, RollingWindowPolicy
from resonance_arbitrage_graph.window_evidence import make_window_regime_evidence_receipt
from resonance_arbitrage_graph.window_regime import market_key


_ZERO = CostAssumption(fee_bps=0.0, slippage_bps=0.0)


def _q(symbol: str, base: str, quote: str, ts: int, mid: float) -> QuoteSnapshot:
    return QuoteSnapshot(
        venue="binance",
        symbol=symbol,
        base_asset=base,
        quote_asset=quote,
        bid_price=mid - 0.01,
        bid_qty=1_000.0,
        ask_price=mid + 0.01,
        ask_qty=1_000.0,
        observed_at_ms=ts,
        source_url=f"fixture:{symbol}",
    )


def _w(symbol: str, base: str, quote: str, mids: list[float]):
    return RollingMarketWindow.from_quotes(
        [_q(symbol, base, quote, ts, mid) for ts, mid in zip((0, 15_000, 30_000, 45_000, 60_000), mids)],
        policy=RollingWindowPolicy(horizon_ms=60_000, min_samples=5, min_coverage_ratio=1.0),
        end_ms=60_000,
    )


def _fixture():
    a = _q("BTCUSDT", "BTC", "USDT", 60_000, 100.0)
    b = _q("ETHBTC", "ETH", "BTC", 60_000, 0.5)
    c = _q("ETHUSDT", "ETH", "USDT", 60_000, 50.0)
    e1, _ = quote_to_trade_edges(a, _ZERO, now_ms=60_000)
    e2, _ = quote_to_trade_edges(b, _ZERO, now_ms=60_000)
    _, e3 = quote_to_trade_edges(c, _ZERO, now_ms=60_000)
    route = (e1, e2, e3)
    windows = {
        market_key("binance", "BTCUSDT"): _w("BTCUSDT", "BTC", "USDT", [100, 100.1, 99.9, 100.2, 100]),
        market_key("binance", "ETHBTC"): _w("ETHBTC", "ETH", "BTC", [0.5, 0.501, 0.499, 0.502, 0.5]),
        market_key("binance", "ETHUSDT"): _w("ETHUSDT", "ETH", "USDT", [50, 50.1, 49.9, 50.2, 50]),
    }
    return (a, b, c), route, evaluate_route(route, 100.0), windows


def test_window_evidence_contains_exact_window_digest_and_samples():
    snapshots, route, result, windows = _fixture()
    receipt = make_window_regime_evidence_receipt(
        "op-window",
        route,
        result,
        snapshots=snapshots,
        windows_by_market=windows,
        evaluation_time_ms=60_000,
    )

    verify_evidence_receipt(receipt)
    state = receipt.payload["rolling_market_state"]
    btc = state["markets"]["binance:BTCUSDT"]
    assert btc["sha256"] == windows["binance:BTCUSDT"].sha256
    assert btc["window"] == windows["binance:BTCUSDT"].canonical_payload()
    assert state["feature_binding"]["short_window_return_volatility_bps"] == "derived_from_rolling_window"


def test_tampered_window_changes_final_evidence_digest():
    snapshots, route, result, windows = _fixture()
    first = make_window_regime_evidence_receipt(
        "op-window",
        route,
        result,
        snapshots=snapshots,
        windows_by_market=windows,
        evaluation_time_ms=60_000,
    )

    original = windows["binance:BTCUSDT"]
    samples = list(original.samples)
    samples[2] = replace(samples[2], bid_price=samples[2].bid_price + 0.001)
    changed = dict(windows)
    changed["binance:BTCUSDT"] = RollingMarketWindow(policy=original.policy, samples=tuple(samples))
    second = make_window_regime_evidence_receipt(
        "op-window",
        route,
        result,
        snapshots=snapshots,
        windows_by_market=changed,
        evaluation_time_ms=60_000,
    )

    assert first.sha256 != second.sha256
