import hashlib

import pytest

from resonance_arbitrage_graph.evidence import EvidenceReceipt
from resonance_arbitrage_graph.observation import OutcomeClass, observation_from_evidence


def _receipt(*, verdict: str, observed_edge: float | None):
    payload = {
        "schema": "resonance.arbitrage.evidence/v0.1",
        "paper_only": True,
        "logical_operation_id": "op-expiry",
        "expected": {"net_edge": 0.002, "verdict": verdict},
    }
    if observed_edge is not None:
        payload["observed"] = {"realized_net_edge": observed_edge}
    draft = EvidenceReceipt(payload=payload, sha256="0" * 64)
    digest = hashlib.sha256(draft.canonical_json().encode("utf-8")).hexdigest()
    return EvidenceReceipt(payload=payload, sha256=digest)


def _make(receipt: EvidenceReceipt, *, expired: bool):
    return observation_from_evidence(
        receipt,
        execution_id="exec-expiry",
        attempt=1,
        opportunity_id="opp-expiry",
        route_id="route-expiry",
        detected_at_ms=10,
        observed_at_ms=20,
        required_edge_bps=10,
        expired=expired,
    )


def test_expired_cannot_hide_realized_outcome():
    with pytest.raises(ValueError, match="cannot have an observed"):
        _make(_receipt(verdict="EXECUTE_SIM", observed_edge=0.0015), expired=True)


def test_observe_candidate_does_not_enter_expired_survival_population():
    observation = _make(_receipt(verdict="OBSERVE", observed_edge=None), expired=True)
    assert observation.outcome_class is OutcomeClass.INDETERMINATE
