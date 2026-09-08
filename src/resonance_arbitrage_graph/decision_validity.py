"""Fail-closed decision-input validity derived from bounded staleness evidence."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .staleness import StalenessAssessment, StalenessVerdict


class DecisionValidityVerdict(str, Enum):
    """Pipeline verdict only; never an order-execution authorization."""

    CONTINUE_CHECKS = "CONTINUE_CHECKS"
    BLOCK = "BLOCK"
    HOLD = "HOLD"


@dataclass(frozen=True, slots=True)
class DecisionValidityAssessment:
    verdict: DecisionValidityVerdict
    staleness_verdict: StalenessVerdict
    reasons: tuple[str, ...]
    execution_authorized: bool = False

    def __post_init__(self) -> None:
        if self.execution_authorized:
            raise ValueError("decision validity cannot authorize execution")


def assess_decision_validity(
    staleness: StalenessAssessment,
) -> DecisionValidityAssessment:
    """Map freshness evidence into a fail-closed downstream-check gate.

    - FRESH: downstream non-execution checks may continue.
    - STALE: the quote input is blocked for this policy evaluation.
    - UNKNOWN: hold; missing/ambiguous evidence is never treated as fresh.

    This function does not evaluate profitability, risk, balances, order state,
    settlement, or any customer-specific trading rule.
    """

    if staleness.verdict is StalenessVerdict.FRESH:
        return DecisionValidityAssessment(
            verdict=DecisionValidityVerdict.CONTINUE_CHECKS,
            staleness_verdict=staleness.verdict,
            reasons=("STALENESS_EVIDENCE_FRESH",),
        )
    if staleness.verdict is StalenessVerdict.STALE:
        return DecisionValidityAssessment(
            verdict=DecisionValidityVerdict.BLOCK,
            staleness_verdict=staleness.verdict,
            reasons=("STALENESS_EVIDENCE_STALE",),
        )
    if staleness.verdict is StalenessVerdict.UNKNOWN:
        return DecisionValidityAssessment(
            verdict=DecisionValidityVerdict.HOLD,
            staleness_verdict=staleness.verdict,
            reasons=("STALENESS_EVIDENCE_UNKNOWN",),
        )
    raise ValueError(f"unsupported staleness verdict: {staleness.verdict!r}")
