from resonance_arbitrage_graph.quotes import QuoteSnapshot
from resonance_arbitrage_graph.scanner import observe_cross_venue_spreads


def test_cross_venue_observer_never_emits_execute_verdict():
    quotes = [
        QuoteSnapshot(
            venue="A",
            symbol="BTCUSDT",
            base_asset="BTC",
            quote_asset="USDT",
            bid_price=99,
            bid_qty=1,
            ask_price=100,
            ask_qty=1,
            observed_at_ms=1,
            source_url="https://a.test",
        ),
        QuoteSnapshot(
            venue="B",
            symbol="BTCUSDT",
            base_asset="BTC",
            quote_asset="USDT",
            bid_price=101,
            bid_qty=1,
            ask_price=102,
            ask_qty=1,
            observed_at_ms=1,
            source_url="https://b.test",
        ),
    ]

    observation = observe_cross_venue_spreads(quotes)[0]
    assert observation.classification.startswith("OBSERVE_ONLY")
    assert not hasattr(observation, "verdict")
