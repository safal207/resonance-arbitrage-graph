import pytest

from resonance_arbitrage_graph import evaluate_route
from resonance_arbitrage_graph.market_evidence import make_market_evidence_receipt
from resonance_arbitrage_graph.quotes import CostAssumption, QuoteSnapshot, quote_to_trade_edges


def snapshot(*, bid_price=80_800, source_url="https://data-api.binance.vision/api/v3/ticker/bookTicker?symbol=BTCUSDT"):
    return QuoteSnapshot(
        venue="BINANCE_SPOT",
        symbol="BTCUSDT",
        base_asset="BTC",
        quote_asset="USDT",
        bid_price=bid_price,
        bid_qty=2,
        ask_price=80_000,
        ask_qty=2,
        observed_at_ms=123456,
        source_url=source_url,
    )


def test_market_evidence_binds_quote_provenance_to_route_edges():
    market = snapshot()
    route = quote_to_trade_edges(market, CostAssumption(fee_bps=0, slippage_bps=0), now_ms=123456)
    result = evaluate_route(route, 1_000)

    receipt = make_market_evidence_receipt("live-001", route, result, snapshots=[market])

    assert receipt.payload["market_data"][0]["source_url"].startswith("https://data-api.binance.vision")
    assert receipt.payload["market_bindings"] == [
        {"edge_index": 0, "snapshot_index": 0, "side": "BUY"},
        {"edge_index": 1, "snapshot_index": 0, "side": "SELL"},
    ]


def test_market_evidence_rejects_snapshot_that_did_not_produce_route():
    original = snapshot()
    route = quote_to_trade_edges(original, CostAssumption(fee_bps=0, slippage_bps=0), now_ms=123456)
    result = evaluate_route(route, 1_000)
    tampered = snapshot(bid_price=80_700)

    with pytest.raises(ValueError, match="not backed by any supplied market snapshot"):
        make_market_evidence_receipt("live-001", route, result, snapshots=[tampered])
