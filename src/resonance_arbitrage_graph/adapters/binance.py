from __future__ import annotations

from collections.abc import Callable
import time
from typing import Any
from urllib.parse import urlencode

from ..quotes import QuoteSnapshot
from .http import get_json


class BinanceBookTickerAdapter:
    """Read-only Binance Spot best-bid/best-ask adapter with verified pair metadata."""

    base_url = "https://data-api.binance.vision"
    metadata_base_url = "https://api.binance.com"
    venue = "BINANCE_SPOT"

    def __init__(self, fetch_json: Callable[[str], dict[str, Any]] | None = None) -> None:
        self._fetch_json = fetch_json or get_json
        self._symbol_metadata: dict[str, tuple[str, str, str]] = {}

    def _metadata(self, symbol: str) -> tuple[str, str, str]:
        cached = self._symbol_metadata.get(symbol)
        if cached is not None:
            return cached

        metadata_url = f"{self.metadata_base_url}/api/v3/exchangeInfo?{urlencode({'symbol': symbol})}"
        payload = self._fetch_json(metadata_url)
        symbols = payload.get("symbols") or []
        if len(symbols) != 1 or symbols[0].get("symbol") != symbol:
            raise ValueError("unexpected Binance exchangeInfo response")

        metadata = symbols[0]
        if metadata.get("status") != "TRADING":
            raise ValueError(f"Binance symbol is not TRADING: {symbol}")
        if metadata.get("isSpotTradingAllowed") is False:
            raise ValueError(f"Binance symbol is not enabled for spot trading: {symbol}")

        base_asset = str(metadata["baseAsset"]).upper()
        quote_asset = str(metadata["quoteAsset"]).upper()
        value = (base_asset, quote_asset, metadata_url)
        self._symbol_metadata[symbol] = value
        return value

    def fetch(self, symbol: str, *, base_asset: str, quote_asset: str) -> QuoteSnapshot:
        if not symbol or not base_asset or not quote_asset:
            raise ValueError("symbol, base_asset and quote_asset must be non-empty")

        normalized_symbol = symbol.upper()
        expected_base = base_asset.upper()
        expected_quote = quote_asset.upper()
        actual_base, actual_quote, metadata_url = self._metadata(normalized_symbol)
        if (actual_base, actual_quote) != (expected_base, expected_quote):
            raise ValueError(
                f"Binance pair metadata mismatch for {normalized_symbol}: "
                f"exchange={actual_base}/{actual_quote}, expected={expected_base}/{expected_quote}"
            )

        url = f"{self.base_url}/api/v3/ticker/bookTicker?{urlencode({'symbol': normalized_symbol})}"
        payload = self._fetch_json(url)
        observed_at_ms = time.time_ns() // 1_000_000

        if payload.get("symbol") != normalized_symbol:
            raise ValueError("unexpected Binance symbol in bookTicker response")

        return QuoteSnapshot(
            venue=self.venue,
            symbol=payload["symbol"],
            base_asset=actual_base,
            quote_asset=actual_quote,
            bid_price=float(payload["bidPrice"]),
            bid_qty=float(payload["bidQty"]),
            ask_price=float(payload["askPrice"]),
            ask_qty=float(payload["askQty"]),
            observed_at_ms=observed_at_ms,
            source_url=url,
            timestamp_class="client_observed",
            source_timestamp_ms=None,
            metadata_url=metadata_url,
        )
