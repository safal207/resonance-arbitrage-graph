import hashlib

import pytest

from resonance_arbitrage_graph.evidence import EvidenceReceipt
from resonance_arbitrage_graph.observation import observation_from_evidence


def _receipt() -> EvidenceReceipt:
    payload = {
        "schema": "resonance.arbitrage.evidence/v0.1",
        "paper_only": True,
        "logical_operation_id": "op-regime",
        "expected": {"net_edge": 0.002, "verdict": "EXECUTE_SIM"},
        "market_regime": {
            "regime": "NORMAL",
            "features": {
                "normalized_spread_bps": 5.0,
                "top_of_book_capacity_ratio": 4.0,
                "quote_age_ms": 100,
                "quote_age_dispersion_ms": 20,
                "cross_rate_dislocation_bps": 5.0,
                "short_window_return_volatility_bps": 20.0,
            },
            "reasons": ["within_normal_thresholds"],
            "policy": {},
        },
    }
    draft = EvidenceReceipt(payload=payload, sha256="0" * 64)
    digest = hashlib.sha256(draft.canonical_json().encode("utf-8")).hexdigest()
    return EvidenceReceipt(payload=payload, sha256=digest)


def test_observation_inherits_evidence_bound_regime_context():
    observation = observation_from_evidence(
        _receipt(),
        execution_id="exec-1",
        attempt=1,
        opportunity_id="opp-1",
        route_id="route-a",
        detected_at_ms=1_000,
        observed_at_ms=1_100,
        market_context={"venue": "binance"},
    )

    assert observation.market_context["venue"] == "binance"
    assert observation.market_context["regime"] == "NORMAL"
    assert observation.market_context["regime_features"]["normalized_spread_bps"] == 5.0


def test_observation_rejects_caller_regime_conflict_with_evidence():
    with pytest.raises(ValueError, match="conflicts with evidence-bound regime"):
        observation_from_evidence(
            _receipt(),
            execution_id="exec-1",
            attempt=1,
            opportunity_id="opp-1",
            route_id="route-a",
            detected_at_ms=1_000,
            observed_at_ms=1_100,
            market_context={"venue": "binance", "regime": "VOLATILE"},
        )
