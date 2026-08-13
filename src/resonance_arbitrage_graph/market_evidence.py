from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from .quotes import QuoteSnapshot


def snapshot_payload(snapshot: QuoteSnapshot) -> dict[str, Any]:
    return {
        "venue": snapshot.venue,
        "symbol": snapshot.symbol,
        "base_asset": snapshot.base_asset,
        "quote_asset": snapshot.quote_asset,
        "bid_price": snapshot.bid_price,
        "bid_qty": snapshot.bid_qty,
        "ask_price": snapshot.ask_price,
        "ask_qty": snapshot.ask_qty,
        "observed_at_ms": snapshot.observed_at_ms,
        "source_timestamp_ms": snapshot.source_timestamp_ms,
        "timestamp_class": snapshot.timestamp_class,
        "source_url": snapshot.source_url,
    }


def snapshots_payload(snapshots: Sequence[QuoteSnapshot]) -> list[dict[str, Any]]:
    return [snapshot_payload(snapshot) for snapshot in snapshots]
