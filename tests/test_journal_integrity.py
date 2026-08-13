import hashlib

import pytest

from resonance_arbitrage_graph.evidence import EvidenceReceipt
from resonance_arbitrage_graph.journal import JournalError, ObservationJournal
from resonance_arbitrage_graph.observation import observation_from_evidence


def _observation(operation_id: str, execution_id: str, attempt: int, observed_edge: float | None):
    payload = {
        "schema": "resonance.arbitrage.evidence/v0.1",
        "paper_only": True,
        "logical_operation_id": operation_id,
        "expected": {"net_edge": 0.002, "verdict": "EXECUTE_SIM"},
    }
    if observed_edge is not None:
        payload["observed"] = {"realized_net_edge": observed_edge}
    draft = EvidenceReceipt(payload=payload, sha256="0" * 64)
    digest = hashlib.sha256(draft.canonical_json().encode("utf-8")).hexdigest()
    receipt = EvidenceReceipt(payload=payload, sha256=digest)
    return observation_from_evidence(
        receipt,
        execution_id=execution_id,
        attempt=attempt,
        opportunity_id="opp-1",
        route_id="route-1",
        detected_at_ms=100,
        observed_at_ms=100 + attempt,
        required_edge_bps=10,
    )


def test_load_rejects_attempt_appended_after_terminal_outcome(tmp_path):
    first = _observation("op-1", "exec-1", 1, 0.0015)
    second = _observation("op-1", "exec-2", 2, 0.0016)
    path = tmp_path / "observations.jsonl"
    path.write_text(
        first.canonical_json() + "\n" + second.canonical_json() + "\n",
        encoding="utf-8",
    )

    with pytest.raises(JournalError, match="terminal outcome"):
        ObservationJournal(path).load()
