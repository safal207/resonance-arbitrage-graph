from __future__ import annotations

from collections.abc import Callable
import time
from typing import Any
from urllib.parse import urlencode

from ..quotes import QuoteSnapshot
from .http import get_json


_ASSET_ALIASES = {
    # Kraken's native code for Bitcoin. RESONANCE uses the cross-venue
    # canonical asset identity BTC while preserving Kraken's raw symbol.
    "XBT": "BTC",
}


def _canonical_asset(value: Any) -> str:
    asset = str(value).strip().upper()
    if not asset:
        raise ValueError("Kraken asset identity must be non-empty")
    return _ASSET_ALIASES.get(asset, asset)


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

        # Kraken documents publication_ts as the time a price level was last
        # updated and published. A resting best level can remain valid while
        # that timestamp becomes old, so it is not a timestamp for the REST
        # snapshot itself. Hard snapshot freshness therefore uses the local
        # observation time. The exact public endpoint remains bound as source
        # provenance; level-update provenance requires a separate future field
        # rather than overloading QuoteSnapshot.source_timestamp_ms.
        return QuoteSnapshot(
            venue=self.venue,
            symbol=str(result.get("symbol") or symbol),
            base_asset=_canonical_asset(result["base_asset"]),
            quote_asset=_canonical_asset(result["quote_asset"]),
            bid_price=float(bid["price"]),
            bid_qty=float(bid["qty"]),
            ask_price=float(ask["price"]),
            ask_qty=float(ask["qty"]),
            observed_at_ms=observed_at_ms,
            source_url=url,
            timestamp_class="client_observed",
            source_timestamp_ms=None,
            metadata_url=url,
        )
