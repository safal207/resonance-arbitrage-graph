from __future__ import annotations

from collections.abc import Sequence

from .engine import PaperExecution
from .evidence import EvidenceReceipt, make_evidence_receipt
from .market_evidence import snapshots_payload
from .model import Edge, RouteResult
from .quotes import QuoteSnapshot


def make_market_evidence_receipt(
    operation_id: str,
    edges: Sequence[Edge],
    result: RouteResult,
    *,
    snapshots: Sequence[QuoteSnapshot],
    execution: PaperExecution | None = None,
) -> EvidenceReceipt:
    """Bind normalized public quote provenance to the existing deterministic receipt."""

    receipt = make_evidence_receipt(
        operation_id,
        edges,
        result,
        execution=execution,
    )
    payload = dict(receipt.payload)
    payload["market_data"] = snapshots_payload(snapshots)

    # Re-use the canonical hashing contract by reconstructing the receipt through
    # the same JSON rules rather than mutating the original digest.
    import hashlib
    import json

    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )
    return EvidenceReceipt(payload=payload, sha256=hashlib.sha256(canonical.encode("utf-8")).hexdigest())
