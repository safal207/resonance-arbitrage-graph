from __future__ import annotations

from collections.abc import Sequence
import hashlib
import json
import math
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
        "metadata_url": snapshot.metadata_url,
    }


def snapshots_payload(snapshots: Sequence[QuoteSnapshot]) -> list[dict[str, Any]]:
    return [snapshot_payload(snapshot) for snapshot in snapshots]


def _edge_snapshot_side(edge: Edge, snapshot: QuoteSnapshot) -> str | None:
    if edge.src.venue != snapshot.venue or edge.dst.venue != snapshot.venue:
        return None

    if edge.src.asset == snapshot.quote_asset and edge.dst.asset == snapshot.base_asset:
        expected_rate = 1.0 / snapshot.ask_price
        expected_capacity = snapshot.ask_price * snapshot.ask_qty
        side = "BUY"
    elif edge.src.asset == snapshot.base_asset and edge.dst.asset == snapshot.quote_asset:
        expected_rate = snapshot.bid_price
        expected_capacity = snapshot.bid_qty
        side = "SELL"
    else:
        return None

    if not math.isclose(edge.rate, expected_rate, rel_tol=1e-12, abs_tol=0.0):
        return None
    if not math.isclose(edge.capacity, expected_capacity, rel_tol=1e-12, abs_tol=0.0):
        return None
    return side


def _bind_route_to_snapshots(
    edges: Sequence[Edge], snapshots: Sequence[QuoteSnapshot]
) -> list[dict[str, Any]]:
    bindings: list[dict[str, Any]] = []
    for edge_index, edge in enumerate(edges):
        matches = [
            (snapshot_index, side)
            for snapshot_index, snapshot in enumerate(snapshots)
            if (side := _edge_snapshot_side(edge, snapshot)) is not None
        ]
        if not matches:
            raise ValueError(f"route edge {edge_index} is not backed by any supplied market snapshot")
        if len(matches) > 1:
            raise ValueError(f"route edge {edge_index} has ambiguous market snapshot provenance")
        snapshot_index, side = matches[0]
        bindings.append(
            {
                "edge_index": edge_index,
                "snapshot_index": snapshot_index,
                "side": side,
            }
        )
    return bindings


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

    bindings = _bind_route_to_snapshots(edges, snapshots)
    receipt = make_evidence_receipt(
        operation_id,
        edges,
        result,
        execution=execution,
    )
    payload = dict(receipt.payload)
    payload["market_data"] = snapshots_payload(snapshots)
    payload["market_bindings"] = bindings

    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return EvidenceReceipt(payload=payload, sha256=digest)
