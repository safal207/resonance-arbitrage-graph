import pytest

from resonance_arbitrage_graph.live_scan import _parse_pair


def test_pair_parser_preserves_exchange_symbol_and_normalizes_assets():
    assert _parse_pair("BTC/USDT:btc:usdt") == ("BTC/USDT", "BTC", "USDT")


def test_pair_parser_rejects_incomplete_pair():
    with pytest.raises(Exception):
        _parse_pair("BTCUSDT:BTC")
