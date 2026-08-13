from __future__ import annotations

from collections.abc import Sequence
import hashlib
import json
from typing import Any

from .engine import PaperExecution
from .evidence import EvidenceReceipt, make_evidence_receipt
from .model import Edge, RouteResult
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


def make_market_evidence_receipt(
    operation_id: str,
    edges: Sequence[Edge],
    result: RouteResult,
    *,
    snapshots: Sequence[QuoteSnapshot],
    execution: PaperExecution | None = None,
) -> EvidenceReceipt:
    """Bind normalized public quote provenance to the deterministic route receipt."""

    if not snapshots:
        raise ValueError("at least one market snapshot is required")

    receipt = make_evidence_receipt(
        operation_id,
        edges,
        result,
        execution=execution,
    )
    payload = dict(receipt.payload)
    payload["market_data"] = snapshots_payload(snapshots)

    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return EvidenceReceipt(payload=payload, sha256=digest)
