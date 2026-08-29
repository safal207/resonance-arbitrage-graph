import pytest

from resonance_arbitrage_graph.adapters import BinanceBookTickerAdapter, KrakenPreTradeAdapter


def test_binance_adapter_verifies_pair_metadata_and_normalizes_book_ticker():
    seen = []

    def fake_fetch(url):
        seen.append(url)
        if "/exchangeInfo?" in url:
            return {
                "symbols": [
                    {
                        "symbol": "BTCUSDT",
                        "status": "TRADING",
                        "baseAsset": "BTC",
                        "quoteAsset": "USDT",
                        "isSpotTradingAllowed": True,
                    }
                ]
            }
        return {
            "symbol": "BTCUSDT",
            "bidPrice": "80000.00",
            "bidQty": "1.25",
            "askPrice": "80001.00",
            "askQty": "0.75",
        }

    quote = BinanceBookTickerAdapter(fetch_json=fake_fetch).fetch(
        "BTCUSDT", base_asset="BTC", quote_asset="USDT"
    )

    assert seen[0].startswith("https://api.binance.com/api/v3/exchangeInfo?")
    assert seen[1].startswith("https://data-api.binance.vision/api/v3/ticker/bookTicker?")
    assert quote.venue == "BINANCE_SPOT"
    assert quote.base_asset == "BTC"
    assert quote.quote_asset == "USDT"
    assert quote.bid_price == 80000.0
    assert quote.ask_price == 80001.0
    assert quote.timestamp_class == "client_observed"
    assert quote.source_timestamp_ms is None
    assert quote.metadata_url and "/exchangeInfo?" in quote.metadata_url


def test_binance_adapter_rejects_caller_pair_label_that_disagrees_with_exchange():
    def fake_fetch(_url):
        return {
            "symbols": [
                {
                    "symbol": "BTCUSDT",
                    "status": "TRADING",
                    "baseAsset": "BTC",
                    "quoteAsset": "USDT",
                    "isSpotTradingAllowed": True,
                }
            ]
        }

    adapter = BinanceBookTickerAdapter(fetch_json=fake_fetch)
    with pytest.raises(ValueError, match="pair metadata mismatch"):
        adapter.fetch("BTCUSDT", base_asset="ETH", quote_asset="USDT")


def test_kraken_adapter_preserves_level_update_time_without_aging_snapshot(monkeypatch):
    observed_at_ms = 2_000_000_000_000
    monkeypatch.setattr(
        "resonance_arbitrage_graph.adapters.kraken.time.time_ns",
        lambda: observed_at_ms * 1_000_000,
    )

    def fake_fetch(_url):
        return {
            "error": [],
            "result": {
                "symbol": "BTC/USDT",
                "base_asset": "BTC",
                "quote_asset": "USDT",
                "bids": [
                    {
                        "side": "BUY",
                        "price": "80010.0",
                        "qty": "2.0",
                        "count": 3,
                        "publication_ts": "2026-08-13T01:00:00.200000Z",
                    }
                ],
                "asks": [
                    {
                        "side": "SELL",
                        "price": "80020.0",
                        "qty": "1.5",
                        "count": 2,
                        "publication_ts": "2026-08-13T01:00:00.300000Z",
                    }
                ],
            },
        }

    quote = KrakenPreTradeAdapter(fetch_json=fake_fetch).fetch("BTC/USDT")

    assert quote.venue == "KRAKEN_SPOT"
    assert quote.base_asset == "BTC"
    assert quote.quote_asset == "USDT"
    assert quote.bid_price == 80010.0
    assert quote.ask_price == 80020.0
    assert quote.timestamp_class == "client_observed_level_update"
    assert quote.source_timestamp_ms is not None
    assert quote.source_timestamp_ms < quote.observed_at_ms
    assert quote.freshness_reference_ms == quote.observed_at_ms
    assert quote.age_ms(observed_at_ms + 250) == 250
    assert quote.metadata_url == quote.source_url
