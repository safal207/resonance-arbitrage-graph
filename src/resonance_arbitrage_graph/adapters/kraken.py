from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
import time
from typing import Any
from urllib.parse import urlencode

from ..quotes import QuoteSnapshot
from .http import get_json


def _iso8601_to_ms(value: str) -> int:
    normalized = value.replace("Z", "+00:00")
    return int(datetime.fromisoformat(normalized).timestamp() * 1000)


class KrakenPreTradeAdapter:
    """Read-only Kraken Spot top-of-book adapter using the public PreTrade feed."""

    base_url = "https://api.kraken.com"
    venue = "KRAKEN_SPOT"

    def __init__(self, fetch_json: Callable[[str], dict[str, Any]] | None = None) -> None:
        self._fetch_json = fetch_json or get_json

    def fetch(self, symbol: str) -> QuoteSnapshot:
        if not symbol:
            raise ValueError("symbol must be non-empty")

        url = f"{self.base_url}/0/public/PreTrade?{urlencode({'symbol': symbol})}"
        payload = self._fetch_json(url)
        observed_at_ms = time.time_ns() // 1_000_000

        errors = payload.get("error") or []
        if errors:
            raise ValueError(f"Kraken returned errors: {errors}")

        result = payload.get("result")
        if not isinstance(result, dict):
            raise ValueError("unexpected Kraken result payload")

        bids = result.get("bids") or []
        asks = result.get("asks") or []
        if not bids or not asks:
            raise ValueError("Kraken response has no top-of-book levels")

        bid = bids[0]
        ask = asks[0]
        publication_times = [
            _iso8601_to_ms(level["publication_ts"])
            for level in (bid, ask)
            if level.get("publication_ts")
        ]
        source_timestamp_ms = min(publication_times) if publication_times else None

        return QuoteSnapshot(
            venue=self.venue,
            symbol=str(result.get("symbol") or symbol),
            base_asset=str(result["base_asset"]).upper(),
            quote_asset=str(result["quote_asset"]).upper(),
            bid_price=float(bid["price"]),
            bid_qty=float(bid["qty"]),
            ask_price=float(ask["price"]),
            ask_qty=float(ask["qty"]),
            observed_at_ms=observed_at_ms,
            source_url=url,
            timestamp_class="exchange_published" if source_timestamp_ms is not None else "client_observed",
            source_timestamp_ms=source_timestamp_ms,
        )
