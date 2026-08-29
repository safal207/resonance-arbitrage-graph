import pytest

from resonance_arbitrage_graph.quotes import CostAssumption, QuoteSnapshot, quote_to_trade_edges


def test_quote_edges_use_top_of_book_capacity_and_freshness():
    quote = QuoteSnapshot(
        venue="BINANCE_SPOT",
        symbol="ETHUSDT",
        base_asset="ETH",
        quote_asset="USDT",
        bid_price=4_000,
        bid_qty=3,
        ask_price=4_001,
        ask_qty=2,
        observed_at_ms=10_000,
        source_url="https://example.test",
    )
    costs = CostAssumption(fee_bps=10, slippage_bps=5)

    buy, sell = quote_to_trade_edges(quote, costs, now_ms=10_250)

    assert buy.src.asset == "USDT"
    assert buy.dst.asset == "ETH"
    assert buy.capacity == 8_002
    assert buy.quote_age_ms == 250
    assert sell.src.asset == "ETH"
    assert sell.dst.asset == "USDT"
    assert sell.capacity == 3
    assert sell.quote_age_ms == 250


def test_exchange_timestamp_is_used_conservatively_for_freshness():
    quote = QuoteSnapshot(
        venue="VENUE_WITH_SNAPSHOT_TIMESTAMP",
        symbol="BTC/USDT",
        base_asset="BTC",
        quote_asset="USDT",
        bid_price=80_000,
        bid_qty=1,
        ask_price=80_010,
        ask_qty=1,
        observed_at_ms=20_000,
        source_timestamp_ms=19_000,
        source_url="https://example.test",
        timestamp_class="exchange_published",
    )

    assert quote.age_ms(20_500) == 1_500


def test_level_update_timestamp_is_preserved_but_not_used_as_snapshot_freshness():
    quote = QuoteSnapshot(
        venue="KRAKEN_SPOT",
        symbol="BTC/USDT",
        base_asset="BTC",
        quote_asset="USDT",
        bid_price=80_000,
        bid_qty=1,
        ask_price=80_010,
        ask_qty=1,
        observed_at_ms=20_000,
        source_timestamp_ms=10_000,
        source_url="https://example.test",
        timestamp_class="client_observed_level_update",
    )

    assert quote.source_timestamp_ms == 10_000
    assert quote.freshness_reference_ms == 20_000
    assert quote.age_ms(20_500) == 500


def test_timestamp_class_cannot_claim_exchange_time_without_source_timestamp():
    with pytest.raises(ValueError, match="require source_timestamp_ms"):
        QuoteSnapshot(
            venue="KRAKEN_SPOT",
            symbol="BTC/USDT",
            base_asset="BTC",
            quote_asset="USDT",
            bid_price=80_000,
            bid_qty=1,
            ask_price=80_010,
            ask_qty=1,
            observed_at_ms=20_000,
            source_url="https://example.test",
            timestamp_class="exchange_published",
        )


def test_level_update_timestamp_class_requires_source_timestamp():
    with pytest.raises(ValueError, match="require source_timestamp_ms"):
        QuoteSnapshot(
            venue="KRAKEN_SPOT",
            symbol="BTC/USDT",
            base_asset="BTC",
            quote_asset="USDT",
            bid_price=80_000,
            bid_qty=1,
            ask_price=80_010,
            ask_qty=1,
            observed_at_ms=20_000,
            source_url="https://example.test",
            timestamp_class="client_observed_level_update",
        )
