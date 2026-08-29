from __future__ import annotations

import pytest

from resonance_arbitrage_graph.adapters.kraken import KrakenPreTradeAdapter
from resonance_arbitrage_graph.live_scan import _fetch_round


def _payload(
    *,
    symbol: str = "XBT/USD",
    base_asset: str = "XBT",
    quote_asset: str = "USD",
):
    return {
        "error": [],
        "result": {
            "symbol": symbol,
            "base_asset": base_asset,
            "quote_asset": quote_asset,
            "bids": [
                {
                    "price": "100.0",
                    "qty": "2.0",
                    "publication_ts": "2026-08-29T00:00:00Z",
                }
            ],
            "asks": [
                {
                    "price": "101.0",
                    "qty": "3.0",
                    "publication_ts": "2026-08-29T00:00:00Z",
                }
            ],
        },
    }


def test_kraken_preserves_raw_symbol_but_canonicalizes_xbt_asset_identity():
    adapter = KrakenPreTradeAdapter(fetch_json=lambda _url: _payload())

    snapshot = adapter.fetch("BTC/USD")

    assert snapshot.symbol == "XBT/USD"
    assert snapshot.base_asset == "BTC"
    assert snapshot.quote_asset == "USD"
    assert "symbol=BTC%2FUSD" in snapshot.source_url


def test_live_round_accepts_cross_venue_btc_identity_for_kraken_xbt():
    adapter = KrakenPreTradeAdapter(fetch_json=lambda _url: _payload())

    snapshots = _fetch_round(adapter, (("BTC/USD", "BTC", "USD"),))

    assert len(snapshots) == 1
    assert (snapshots[0].base_asset, snapshots[0].quote_asset) == ("BTC", "USD")


def test_kraken_asset_canonicalization_does_not_relabel_unrelated_assets():
    adapter = KrakenPreTradeAdapter(
        fetch_json=lambda _url: _payload(
            symbol="ETH/USD",
            base_asset="ETH",
            quote_asset="USD",
        )
    )

    snapshot = adapter.fetch("ETH/USD")

    assert snapshot.base_asset == "ETH"
    assert snapshot.quote_asset == "USD"


def test_live_round_still_rejects_wrong_expected_asset_after_alias_normalization():
    adapter = KrakenPreTradeAdapter(fetch_json=lambda _url: _payload())

    with pytest.raises(ValueError, match="normalized pair mismatch"):
        _fetch_round(adapter, (("BTC/USD", "XBT", "USD"),))
