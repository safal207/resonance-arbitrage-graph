from resonance_arbitrage_graph import evaluate_route
from resonance_arbitrage_graph.market_evidence import make_market_evidence_receipt
from resonance_arbitrage_graph.quotes import CostAssumption, QuoteSnapshot, quote_to_trade_edges


def snapshot(source_url):
    return QuoteSnapshot(
        venue="BINANCE_SPOT",
        symbol="BTCUSDT",
        base_asset="BTC",
        quote_asset="USDT",
        bid_price=80_800,
        bid_qty=2,
        ask_price=80_000,
        ask_qty=2,
        observed_at_ms=123456,
        source_url=source_url,
    )


def test_market_evidence_digest_changes_with_quote_source():
    first_snapshot = snapshot("https://a.test")
    second_snapshot = snapshot("https://b.test")
    route = quote_to_trade_edges(
        first_snapshot,
        CostAssumption(fee_bps=0, slippage_bps=0),
        now_ms=123456,
    )
    result = evaluate_route(route, 1_000)

    first = make_market_evidence_receipt("live-001", route, result, snapshots=[first_snapshot])
    second = make_market_evidence_receipt("live-001", route, result, snapshots=[second_snapshot])

    assert first.sha256 != second.sha256
