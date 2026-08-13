from __future__ import annotations

from collections.abc import Callable
import time
from typing import Any
from urllib.parse import urlencode

from ..quotes import QuoteSnapshot
from .http import get_json


class BinanceBookTickerAdapter:
    """Read-only Binance Spot best-bid/best-ask adapter."""

    base_url = "https://data-api.binance.vision"
    venue = "BINANCE_SPOT"

    def __init__(self, fetch_json: Callable[[str], dict[str, Any]] | None = None) -> None:
        self._fetch_json = fetch_json or get_json

    def fetch(self, symbol: str, *, base_asset: str, quote_asset: str) -> QuoteSnapshot:
        if not symbol or not base_asset or not quote_asset:
            raise ValueError("symbol, base_asset and quote_asset must be non-empty")

        url = f"{self.base_url}/api/v3/ticker/bookTicker?{urlencode({'symbol': symbol.upper()})}"
        payload = self._fetch_json(url)
        observed_at_ms = time.time_ns() // 1_000_000

        if payload.get("symbol") != symbol.upper():
            raise ValueError("unexpected Binance symbol in response")

        return QuoteSnapshot(
            venue=self.venue,
            symbol=payload["symbol"],
            base_asset=base_asset.upper(),
            quote_asset=quote_asset.upper(),
            bid_price=float(payload["bidPrice"]),
            bid_qty=float(payload["bidQty"]),
            ask_price=float(payload["askPrice"]),
            ask_qty=float(payload["askQty"]),
            observed_at_ms=observed_at_ms,
            source_url=url,
            timestamp_class="client_observed",
            source_timestamp_ms=None,
        )
