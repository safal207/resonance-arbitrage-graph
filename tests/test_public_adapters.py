from resonance_arbitrage_graph.adapters import BinanceBookTickerAdapter, KrakenPreTradeAdapter


def test_binance_adapter_normalizes_book_ticker_without_auth():
    seen = []

    def fake_fetch(url):
        seen.append(url)
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

    assert seen and seen[0].startswith("https://data-api.binance.vision/api/v3/ticker/bookTicker?")
    assert quote.venue == "BINANCE_SPOT"
    assert quote.base_asset == "BTC"
    assert quote.quote_asset == "USDT"
    assert quote.bid_price == 80000.0
    assert quote.ask_price == 80001.0
    assert quote.timestamp_class == "client_observed"
    assert quote.source_timestamp_ms is None


def test_kraken_adapter_uses_exchange_publication_timestamp():
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
    assert quote.timestamp_class == "exchange_published"
    assert quote.source_timestamp_ms is not None
