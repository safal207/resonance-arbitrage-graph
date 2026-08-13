from resonance_arbitrage_graph.observation import OpportunityObservation, OutcomeClass
from resonance_arbitrage_graph.reliability import (
    RankingCandidate,
    RankingStatus,
    build_reliability_profile,
    score_candidate,
)


_SHA = "b" * 64


def _obs(op: str, *, regime: str, outcome: OutcomeClass) -> OpportunityObservation:
    observed = 15.0 if outcome is OutcomeClass.TRUE_POSITIVE else 0.0
    if outcome is OutcomeClass.EXPIRED:
        observed = None
    return OpportunityObservation(
        logical_operation_id=op,
        execution_id=f"exec-{op}",
        attempt=1,
        opportunity_id=f"opp-{op}",
        route_id="route-a",
        detected_at_ms=1_000,
        observed_at_ms=1_100,
        expected_verdict="EXECUTE_SIM",
        required_edge_bps=10.0,
        expected_edge_bps=20.0,
        observed_edge_bps=observed,
        outcome_class=outcome,
        evidence_sha256=_SHA,
        market_context={"venue": "binance", "regime": regime},
    )


def test_exact_regime_segmentation_prevents_cross_regime_history_leakage():
    observations = [
        _obs("normal-good", regime="NORMAL", outcome=OutcomeClass.TRUE_POSITIVE),
        _obs("volatile-bad", regime="VOLATILE", outcome=OutcomeClass.FALSE_POSITIVE),
    ]

    profile = build_reliability_profile(
        observations,
        route_id="route-a",
        market_context={"venue": "binance", "regime": "NORMAL"},
    )

    assert profile.matched_operations == 1
    assert profile.true_positive == 1
    assert profile.false_positive == 0


def test_unknown_regime_candidate_is_ineligible():
    candidate = RankingCandidate(
        candidate_id="candidate-a",
        route_id="route-a",
        raw_edge_bps=20.0,
        verifier_verdict="EXECUTE_SIM",
        market_context={"venue": "binance", "regime": "UNKNOWN"},
    )

    score = score_candidate(candidate, [])

    assert score.status is RankingStatus.INELIGIBLE
    assert score.adjusted_score_bps == 0.0
    assert "unknown_market_regime" in score.reasons
