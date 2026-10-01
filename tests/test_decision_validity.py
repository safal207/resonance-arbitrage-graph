from __future__ import annotations

import pytest

from resonance_arbitrage_graph.decision_validity import (
    DecisionValidityAssessment,
    DecisionValidityVerdict,
    assess_decision_validity,
)
from resonance_arbitrage_graph.staleness import StalenessAssessment, StalenessVerdict


def assessment(verdict: StalenessVerdict) -> StalenessAssessment:
    return StalenessAssessment(
        verdict=verdict,
        observation_age_ms=1,
        source_age_ms=None,
        reasons=("TEST",),
        timestamp_class="client_observed",
        max_observation_age_ms=10,
        max_source_age_ms=None,
    )


def test_fresh_only_continues_downstream_checks() -> None:
    result = assess_decision_validity(assessment(StalenessVerdict.FRESH))
    assert result.verdict is DecisionValidityVerdict.CONTINUE_CHECKS
    assert result.reasons == ("STALENESS_EVIDENCE_FRESH",)
    assert result.execution_authorized is False


def test_stale_blocks_input() -> None:
    result = assess_decision_validity(assessment(StalenessVerdict.STALE))
    assert result.verdict is DecisionValidityVerdict.BLOCK
    assert result.reasons == ("STALENESS_EVIDENCE_STALE",)
    assert result.execution_authorized is False


def test_unknown_holds_fail_closed() -> None:
    result = assess_decision_validity(assessment(StalenessVerdict.UNKNOWN))
    assert result.verdict is DecisionValidityVerdict.HOLD
    assert result.reasons == ("STALENESS_EVIDENCE_UNKNOWN",)
    assert result.execution_authorized is False


def test_decision_validity_cannot_authorize_execution() -> None:
    with pytest.raises(ValueError):
        DecisionValidityAssessment(
            verdict=DecisionValidityVerdict.CONTINUE_CHECKS,
            staleness_verdict=StalenessVerdict.FRESH,
            reasons=("TEST",),
            execution_authorized=True,
        )
