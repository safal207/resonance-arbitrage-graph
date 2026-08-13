import hashlib
import json

import pytest

from resonance_arbitrage_graph.evidence import EvidenceReceipt
from resonance_arbitrage_graph.model import Verdict
from resonance_arbitrage_graph.observation import observation_from_evidence
from resonance_arbitrage_graph.regime import MarketRegime
from resonance_arbitrage_graph.regime_gate import RegimeExecutionPolicy, apply_regime_gate


def _receipt(payload):
    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )
    return EvidenceReceipt(
        payload=payload,
        sha256=hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
    )


def test_evidence_gate_object_must_be_structurally_canonical_even_with_valid_hash():
    policy = RegimeExecutionPolicy()
    gate = apply_regime_gate(Verdict.EXECUTE_SIM, MarketRegime.NORMAL, policy=policy)
    gate_payload = {**gate.to_payload(), "policy": policy.canonical_payload()}
    gate_payload.pop("reasons")
    receipt = _receipt(
        {
            "paper_only": True,
            "logical_operation_id": "canonical-gate",
            "expected": {
                "verdict": "EXECUTE_SIM",
                "base_verdict": "EXECUTE_SIM",
                "net_edge": 0.004,
            },
            "market_regime": {
                "regime": "NORMAL",
                "features": {},
                "reasons": ["normal"],
            },
            "regime_execution_gate": gate_payload,
        }
    )

    with pytest.raises(ValueError, match="fields are not canonical"):
        observation_from_evidence(
            receipt,
            execution_id="exec",
            attempt=1,
            opportunity_id="opp",
            route_id="route",
            detected_at_ms=1,
            observed_at_ms=2,
            required_edge_bps=30.0,
        )
