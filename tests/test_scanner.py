from resonance_arbitrage_graph import Node, Verdict
from resonance_arbitrage_graph.quotes import CostAssumption, QuoteSnapshot
from resonance_arbitrage_graph.scanner import observe_cross_venue_spreads, scan_cycles


def q(symbol, base, quote, bid, bid_qty, ask, ask_qty, venue="BINANCE_SPOT"):
    return QuoteSnapshot(
        venue=venue,
        symbol=symbol,
        base_asset=base,
        quote_asset=quote,
        bid_price=bid,
        bid_qty=bid_qty,
        ask_price=ask,
        ask_qty=ask_qty,
        observed_at_ms=10_000,
        source_url="https://example.test",
    )


def test_real_quote_shape_can_form_profitable_triangular_cycle():
    quotes = [
        q("BTCUSDT", "BTC", "USDT", 79_990, 10, 80_000, 10),
        q("ETHBTC", "ETH", "BTC", 0.0499, 100, 0.05, 100),
        q("ETHUSDT", "ETH", "USDT", 4_100, 100, 4_101, 100),
    ]

    results = scan_cycles(
        quotes,
        start=Node("BINANCE_SPOT", "USDT"),
        amount=1_000,
        costs_by_venue={"BINANCE_SPOT": CostAssumption(fee_bps=5, slippage_bps=5)},
        now_ms=10_100,
        max_hops=3,
    )

    assert results
    assert results[0].result.verdict is Verdict.EXECUTE_SIM
    assert results[0].result.net_edge > 0
    assert len(results[0].route) == 3


def test_missing_fee_assumptions_fail_closed():
    quotes = [q("BTCUSDT", "BTC", "USDT", 79_990, 10, 80_000, 10)]

    try:
        scan_cycles(
            quotes,
            start=Node("BINANCE_SPOT", "USDT"),
            amount=1_000,
            costs_by_venue={},
            now_ms=10_100,
        )
    except ValueError as exc:
        assert "missing explicit cost assumptions" in str(exc)
    else:
        raise AssertionError("scanner must fail closed when venue costs are unspecified")


def test_cross_venue_gap_is_observe_only_without_rebalance_model():
    quotes = [
        q("BTCUSDT", "BTC", "USDT", 99.0, 10, 100.0, 10, venue="VENUE_A"),
        q("BTCUSDT", "BTC", "USDT", 101.0, 10, 102.0, 10, venue="VENUE_B"),
    ]

    observations = observe_cross_venue_spreads(quotes)

    assert len(observations) == 1
    assert observations[0].buy_venue == "VENUE_A"
    assert observations[0].sell_venue == "VENUE_B"
    assert observations[0].gross_edge > 0
    assert observations[0].classification == "OBSERVE_ONLY_REBALANCE_UNMODELED"
