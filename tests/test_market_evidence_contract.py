from resonance_arbitrage_graph import Edge, Node, evaluate_route
from resonance_arbitrage_graph.market_evidence import make_market_evidence_receipt
from resonance_arbitrage_graph.quotes import QuoteSnapshot


def test_market_evidence_binds_quote_provenance_to_digest():
    a = Node("BINANCE_SPOT", "USDT")
    b = Node("BINANCE_SPOT", "BTC")
    route = [Edge(a, b, rate=1 / 80_000), Edge(b, a, rate=80_800)]
    result = evaluate_route(route, 1_000)
    snapshot = QuoteSnapshot(
        venue="BINANCE_SPOT",
        symbol="BTCUSDT",
        base_asset="BTC",
        quote_asset="USDT",
        bid_price=80_800,
        bid_qty=2,
        ask_price=80_000,
        ask_qty=2,
        observed_at_ms=123456,
        source_url="https://data-api.binance.vision/api/v3/ticker/bookTicker?symbol=BTCUSDT",
    )

    receipt = make_market_evidence_receipt("live-001", route, result, snapshots=[snapshot])

    assert receipt.payload["market_data"][0]["source_url"].startswith("https://data-api.binance.vision")
    assert receipt.payload["market_data"][0]["symbol"] == "BTCUSDT"
    assert receipt.payload["market_data"][0]["timestamp_class"] == "client_observed"
