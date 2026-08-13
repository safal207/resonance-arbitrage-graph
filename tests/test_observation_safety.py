import hashlib

import pytest

from resonance_arbitrage_graph.evidence import EvidenceReceipt
from resonance_arbitrage_graph.observation import observation_from_evidence


def test_observation_memory_rejects_non_paper_evidence():
    payload = {
        "schema": "resonance.arbitrage.evidence/v0.1",
        "paper_only": False,
        "logical_operation_id": "op-live",
        "expected": {"net_edge": 0.001, "verdict": "EXECUTE_SIM"},
    }
    draft = EvidenceReceipt(payload=payload, sha256="0" * 64)
    digest = hashlib.sha256(draft.canonical_json().encode("utf-8")).hexdigest()
    receipt = EvidenceReceipt(payload=payload, sha256=digest)

    with pytest.raises(ValueError, match="paper-only"):
        observation_from_evidence(
            receipt,
            execution_id="exec-live",
            attempt=1,
            opportunity_id="opp-live",
            route_id="route-live",
            detected_at_ms=1,
            observed_at_ms=2,
        )
