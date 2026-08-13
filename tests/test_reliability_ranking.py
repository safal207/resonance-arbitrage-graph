import pytest

from resonance_arbitrage_graph.observation import OpportunityObservation, OutcomeClass
from resonance_arbitrage_graph.reliability import (
    RankingCandidate,
    RankingStatus,
    ReliabilityPolicy,
    build_reliability_profile,
    rank_candidates,
    score_candidate,
)


_SHA = "a" * 64


def _obs(
    op: str,
    execution: str,
    attempt: int,
    *,
    route: str = "route-a",
    venue: str = "binance",
    regime: str = "normal",
    outcome: OutcomeClass = OutcomeClass.TRUE_POSITIVE,
    expected_bps: float = 20.0,
    observed_bps: float | None = 15.0,
    detected: int = 1_000,
) -> OpportunityObservation:
    if outcome is OutcomeClass.EXPIRED:
        observed_bps = None
    if outcome is OutcomeClass.INDETERMINATE:
        observed_bps = None
    expected_verdict = "EXECUTE_SIM"
    required_bps = 10.0
    if outcome is OutcomeClass.REJECTED:
        expected_verdict = "REJECT"
        observed_bps = None
    return OpportunityObservation(
        logical_operation_id=op,
        execution_id=execution,
        attempt=attempt,
        opportunity_id=f"opp-{op}",
        route_id=route,
        detected_at_ms=detected,
        observed_at_ms=detected + attempt * 100,
        expected_verdict=expected_verdict,
        required_edge_bps=required_bps,
        expected_edge_bps=expected_bps,
        observed_edge_bps=observed_bps,
        outcome_class=outcome,
        evidence_sha256=_SHA,
        market_context={"venue": venue, "regime": regime},
    )


def _candidate(
    candidate_id: str = "candidate-a",
    *,
    route: str = "route-a",
    raw_bps: float = 20.0,
    verdict: str = "EXECUTE_SIM",
    venue: str = "binance",
    regime: str = "normal",
) -> RankingCandidate:
    return RankingCandidate(
        candidate_id=candidate_id,
        route_id=route,
        raw_edge_bps=raw_bps,
        verifier_verdict=verdict,
        market_context={"venue": venue, "regime": regime},
    )


def test_low_sample_truth_rate_is_smoothed_and_not_rankable():
    observations = [_obs("op-1", "exec-1", 1)]
    policy = ReliabilityPolicy(min_truth_samples=3, min_history_samples=4)

    profile = build_reliability_profile(
        observations,
        route_id="route-a",
        market_context={"venue": "binance", "regime": "normal"},
        policy=policy,
    )
    score = score_candidate(_candidate(), observations, policy=policy)

    assert profile.truth_samples == 1
    assert profile.smoothed_truth_rate == pytest.approx(3 / 5)
    assert profile.history_confidence == pytest.approx(0.25)
    assert score.status is RankingStatus.INSUFFICIENT_HISTORY
    assert score.adjusted_score_bps == 0.0
    assert score.provisional_score_bps > 0.0


def test_history_can_never_promote_non_positive_raw_edge():
    observations = [
        _obs(f"op-{i}", f"exec-{i}", 1, expected_bps=10.0, observed_bps=30.0)
        for i in range(1, 6)
    ]

    score = score_candidate(_candidate(raw_bps=-1.0), observations)

    assert score.status is RankingStatus.INELIGIBLE
    assert score.adjusted_score_bps == 0.0
    assert score.bias_penalty_bps == 0.0
    assert score.bias_adjusted_edge_bps == 0.0
    assert "non_positive_raw_edge" in score.reasons


def test_positive_prediction_bias_does_not_increase_current_edge():
    observations = [
        _obs(f"op-{i}", f"exec-{i}", 1, expected_bps=10.0, observed_bps=25.0)
        for i in range(1, 6)
    ]

    score = score_candidate(_candidate(raw_bps=20.0), observations)

    assert score.status is RankingStatus.RANKED
    assert score.profile.mean_prediction_error_bps == pytest.approx(15.0)
    assert score.bias_penalty_bps == 0.0
    assert score.bias_adjusted_edge_bps == pytest.approx(20.0)


def test_negative_prediction_bias_reduces_or_suppresses_edge():
    observations = [
        _obs(f"op-{i}", f"exec-{i}", 1, expected_bps=20.0, observed_bps=5.0, outcome=OutcomeClass.FALSE_POSITIVE)
        for i in range(1, 6)
    ]

    reduced = score_candidate(_candidate(raw_bps=30.0), observations)
    suppressed = score_candidate(_candidate(candidate_id="small", raw_bps=10.0), observations)

    assert reduced.bias_penalty_bps == pytest.approx(-15.0)
    assert reduced.bias_adjusted_edge_bps == pytest.approx(15.0)
    assert reduced.status is RankingStatus.RANKED
    assert suppressed.bias_adjusted_edge_bps == 0.0
    assert suppressed.status is RankingStatus.SUPPRESSED_BY_HISTORY


def test_segment_filter_prevents_route_and_context_leakage():
    observations = [
        _obs("binance-good", "exec-1", 1, venue="binance", outcome=OutcomeClass.TRUE_POSITIVE),
        _obs("kraken-bad", "exec-2", 1, venue="kraken", outcome=OutcomeClass.FALSE_POSITIVE, observed_bps=0.0),
        _obs("other-route", "exec-3", 1, route="route-b", venue="binance", outcome=OutcomeClass.FALSE_POSITIVE, observed_bps=0.0),
    ]

    profile = build_reliability_profile(
        observations,
        route_id="route-a",
        market_context={"venue": "binance", "regime": "normal"},
    )

    assert profile.matched_operations == 1
    assert profile.true_positive == 1
    assert profile.false_positive == 0


def test_retry_history_is_collapsed_by_logical_operation():
    observations = [
        _obs("op-1", "exec-1", 1, outcome=OutcomeClass.INDETERMINATE),
        _obs("op-1", "exec-2", 2, outcome=OutcomeClass.TRUE_POSITIVE),
    ]

    profile = build_reliability_profile(
        observations,
        route_id="route-a",
        market_context={"venue": "binance", "regime": "normal"},
    )

    assert profile.matched_operations == 1
    assert profile.truth_samples == 1
    assert profile.true_positive == 1


def test_non_execute_verdict_is_never_promoted_by_reliability():
    observations = [
        _obs(f"op-{i}", f"exec-{i}", 1)
        for i in range(1, 6)
    ]

    score = score_candidate(
        _candidate(verdict="OBSERVE_ONLY_REBALANCE_UNMODELED", raw_bps=100.0),
        observations,
    )

    assert score.status is RankingStatus.INELIGIBLE
    assert score.adjusted_score_bps == 0.0
    assert "verifier_not_execute_sim" in score.reasons


def test_ranking_is_deterministic_with_stable_tie_breaking():
    observations = [
        _obs(f"op-{i}", f"exec-{i}", 1)
        for i in range(1, 6)
    ]
    candidates = [
        _candidate("b", raw_bps=20.0),
        _candidate("a", raw_bps=20.0),
    ]

    first = rank_candidates(candidates, observations)
    second = rank_candidates(reversed(candidates), observations)

    assert [item.candidate_id for item in first] == ["a", "b"]
    assert [item.candidate_id for item in second] == ["a", "b"]


def test_missing_segment_key_fails_closed():
    candidate = RankingCandidate(
        candidate_id="candidate-a",
        route_id="route-a",
        raw_edge_bps=20.0,
        verifier_verdict="EXECUTE_SIM",
        market_context={"venue": "binance"},
    )

    with pytest.raises(ValueError, match="missing segment key"):
        score_candidate(candidate, [])
