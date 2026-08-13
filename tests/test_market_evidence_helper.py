from resonance_arbitrage_graph import Edge, Node, evaluate_route
from resonance_arbitrage_graph.evidence_ext import make_market_evidence_receipt
from resonance_arbitrage_graph.quotes import QuoteSnapshot


def test_market_evidence_digest_changes_with_quote_source():
    a = Node("BINANCE_SPOT", "USDT")
    b = Node("BINANCE_SPOT", "BTC")
    route = [Edge(a, b, rate=1 / 80_000), Edge(b, a, rate=80_800)]
    result = evaluate_route(route, 1_000)

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

    first = make_market_evidence_receipt("live-001", route, result, snapshots=[snapshot("https://a.test")])
    second = make_market_evidence_receipt("live-001", route, result, snapshots=[snapshot("https://b.test")])

    assert first.sha256 != second.sha256
