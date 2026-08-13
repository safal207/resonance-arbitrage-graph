from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
import math
from collections.abc import Sequence
from typing import Any

from .engine import PaperExecution
from .model import Edge, RouteResult


@dataclass(frozen=True, slots=True)
class EvidenceReceipt:
    payload: dict[str, Any]
    sha256: str

    def canonical_json(self) -> str:
        return json.dumps(
            self.payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )


def _finite_or_none(value: float) -> float | None:
    return value if math.isfinite(value) else None


def _edge_payload(edge: Edge) -> dict[str, Any]:
    return {
        "src": edge.src.key,
        "dst": edge.dst.key,
        "rate": edge.rate,
        "fee_bps": edge.fee_bps,
        "slippage_bps": edge.slippage_bps,
        "gas_bps": edge.gas_bps,
        "capacity": _finite_or_none(edge.capacity),
        "latency_ms": edge.latency_ms,
        "quote_age_ms": edge.quote_age_ms,
        "failure_probability": edge.failure_probability,
        "settlement_probability": edge.settlement_probability,
        "confidence": edge.confidence,
    }


def make_evidence_receipt(
    operation_id: str,
    edges: Sequence[Edge],
    result: RouteResult,
    *,
    execution: PaperExecution | None = None,
) -> EvidenceReceipt:
    if not operation_id:
        raise ValueError("operation_id must be non-empty")

    if execution is not None:
        if execution.operation_id != operation_id:
            raise ValueError("execution operation_id does not match evidence operation_id")
        if execution.expected != result:
            raise ValueError("execution expected result does not match evidence result")

    payload: dict[str, Any] = {
        "schema": "resonance.arbitrage.evidence/v0.1",
        "paper_only": True,
        "logical_operation_id": operation_id,
        "causal_spine": [
            "market_state",
            "discrepancy",
            "candidate_route",
            "execution_constraints",
            "state_transitions",
            "settlement",
            "paper_pnl",
            "evidence",
        ],
        "route": [_edge_payload(edge) for edge in edges],
        "expected": {
            **asdict(result),
            "verdict": result.verdict.value,
        },
        "invariants": {
            "returns_to_start": bool(edges) and edges[-1].dst == edges[0].src,
            "positive_net_edge": result.net_edge > 0,
            "constraints_satisfied": not result.reasons,
        },
    }

    if execution is not None:
        payload["observed"] = {
            "realized_final_amount": execution.realized_final_amount,
            "realized_net_edge": execution.realized_net_edge,
            "prediction_error": execution.prediction_error,
        }

    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return EvidenceReceipt(payload=payload, sha256=digest)
