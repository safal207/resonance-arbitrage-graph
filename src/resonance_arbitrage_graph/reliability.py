from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import json
import math
from statistics import mean
from typing import Any, Iterable

from .journal import collapse_operations
from .observation import OpportunityObservation, OutcomeClass


class RankingStatus(str, Enum):
    RANKED = "RANKED"
    INSUFFICIENT_HISTORY = "INSUFFICIENT_HISTORY"
    SUPPRESSED_BY_HISTORY = "SUPPRESSED_BY_HISTORY"
    INELIGIBLE = "INELIGIBLE"


@dataclass(frozen=True, slots=True)
class ReliabilityPolicy:
    truth_prior_alpha: float = 2.0
    truth_prior_beta: float = 2.0
    survival_prior_alpha: float = 2.0
    survival_prior_beta: float = 2.0
    min_truth_samples: int = 3
    min_history_samples: int = 4

    def __post_init__(self) -> None:
        for name in (
            "truth_prior_alpha",
            "truth_prior_beta",
            "survival_prior_alpha",
            "survival_prior_beta",
        ):
            value = getattr(self, name)
            if not math.isfinite(value) or value <= 0:
                raise ValueError(f"{name} must be finite and positive")
        if self.min_truth_samples < 1:
            raise ValueError("min_truth_samples must be >= 1")
        if self.min_history_samples < self.min_truth_samples:
            raise ValueError("min_history_samples must be >= min_truth_samples")


@dataclass(frozen=True, slots=True)
class RankingCandidate:
    candidate_id: str
    route_id: str
    raw_edge_bps: float
    verifier_verdict: str
    market_context: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.candidate_id or not self.route_id:
            raise ValueError("candidate_id and route_id must be non-empty")
        if not self.verifier_verdict:
            raise ValueError("verifier_verdict must be non-empty")
        if not math.isfinite(self.raw_edge_bps):
            raise ValueError("raw_edge_bps must be finite")
        context = dict(self.market_context)
        try:
            json.dumps(context, sort_keys=True, allow_nan=False)
        except (TypeError, ValueError) as exc:
            raise ValueError("market_context must be strict JSON") from exc
        object.__setattr__(self, "market_context", context)


@dataclass(frozen=True, slots=True)
class ReliabilityProfile:
    route_id: str
    segment: dict[str, Any]
    matched_operations: int
    truth_samples: int
    true_positive: int
    false_positive: int
    expired: int
    smoothed_truth_rate: float
    smoothed_survival_rate: float
    history_confidence: float
    mean_prediction_error_bps: float | None

    @property
    def history_samples(self) -> int:
        return self.truth_samples + self.expired


@dataclass(frozen=True, slots=True)
class ReliabilityAdjustedScore:
    candidate_id: str
    route_id: str
    status: RankingStatus
    raw_edge_bps: float
    bias_penalty_bps: float
    bias_adjusted_edge_bps: float
    truth_probability: float
    survival_probability: float
    history_confidence: float
    provisional_score_bps: float
    adjusted_score_bps: float
    profile: ReliabilityProfile
    reasons: tuple[str, ...]


def _segment_context(
    market_context: dict[str, Any],
    segment_keys: tuple[str, ...],
) -> dict[str, Any]:
    if len(set(segment_keys)) != len(segment_keys):
        raise ValueError("segment_keys must be unique")
    segment: dict[str, Any] = {}
    for key in segment_keys:
        if not key:
            raise ValueError("segment_keys cannot contain empty keys")
        if key not in market_context:
            raise ValueError(f"candidate market_context is missing segment key: {key}")
        segment[key] = market_context[key]
    return segment


def _matches_segment(
    observation: OpportunityObservation,
    *,
    route_id: str,
    segment: dict[str, Any],
) -> bool:
    if observation.route_id != route_id:
        return False
    return all(
        key in observation.market_context
        and observation.market_context[key] == value
        for key, value in segment.items()
    )


def build_reliability_profile(
    observations: list[OpportunityObservation],
    *,
    route_id: str,
    market_context: dict[str, Any],
    segment_keys: tuple[str, ...] = ("venue", "regime"),
    policy: ReliabilityPolicy | None = None,
) -> ReliabilityProfile:
    if not route_id:
        raise ValueError("route_id must be non-empty")
    policy = policy or ReliabilityPolicy()
    segment = _segment_context(dict(market_context), segment_keys)
    collapsed = collapse_operations(observations)
    matched = [
        observation
        for observation in collapsed
        if _matches_segment(observation, route_id=route_id, segment=segment)
    ]

    true_positive = sum(
        observation.outcome_class is OutcomeClass.TRUE_POSITIVE
        for observation in matched
    )
    false_positive = sum(
        observation.outcome_class is OutcomeClass.FALSE_POSITIVE
        for observation in matched
    )
    expired = sum(
        observation.outcome_class is OutcomeClass.EXPIRED
        for observation in matched
    )
    truth_samples = true_positive + false_positive
    history_samples = truth_samples + expired

    truth_rate = (
        true_positive + policy.truth_prior_alpha
    ) / (
        truth_samples + policy.truth_prior_alpha + policy.truth_prior_beta
    )
    survival_rate = (
        truth_samples + policy.survival_prior_alpha
    ) / (
        history_samples + policy.survival_prior_alpha + policy.survival_prior_beta
    )
    confidence = min(1.0, history_samples / policy.min_history_samples)

    errors = [
        observation.prediction_error_bps
        for observation in matched
        if observation.outcome_class in {
            OutcomeClass.TRUE_POSITIVE,
            OutcomeClass.FALSE_POSITIVE,
        }
        and observation.prediction_error_bps is not None
    ]

    return ReliabilityProfile(
        route_id=route_id,
        segment=segment,
        matched_operations=len(matched),
        truth_samples=truth_samples,
        true_positive=true_positive,
        false_positive=false_positive,
        expired=expired,
        smoothed_truth_rate=truth_rate,
        smoothed_survival_rate=survival_rate,
        history_confidence=confidence,
        mean_prediction_error_bps=mean(errors) if errors else None,
    )


def score_candidate(
    candidate: RankingCandidate,
    observations: list[OpportunityObservation],
    *,
    segment_keys: tuple[str, ...] = ("venue", "regime"),
    policy: ReliabilityPolicy | None = None,
) -> ReliabilityAdjustedScore:
    policy = policy or ReliabilityPolicy()
    profile = build_reliability_profile(
        observations,
        route_id=candidate.route_id,
        market_context=candidate.market_context,
        segment_keys=segment_keys,
        policy=policy,
    )

    reasons: list[str] = []
    if candidate.verifier_verdict != "EXECUTE_SIM":
        reasons.append("verifier_not_execute_sim")
    if candidate.raw_edge_bps <= 0:
        reasons.append("non_positive_raw_edge")
    if "regime" in segment_keys and candidate.market_context.get("regime") == "UNKNOWN":
        reasons.append("unknown_market_regime")

    mean_error = profile.mean_prediction_error_bps
    bias_penalty = min(0.0, mean_error if mean_error is not None else 0.0)
    bias_adjusted = max(0.0, candidate.raw_edge_bps + bias_penalty)

    provisional = (
        bias_adjusted
        * profile.smoothed_truth_rate
        * profile.smoothed_survival_rate
        * profile.history_confidence
    )

    if reasons:
        status = RankingStatus.INELIGIBLE
        adjusted = 0.0
    elif bias_adjusted <= 0:
        status = RankingStatus.SUPPRESSED_BY_HISTORY
        adjusted = 0.0
        reasons.append("historical_negative_bias_consumed_edge")
    elif (
        profile.truth_samples < policy.min_truth_samples
        or profile.history_samples < policy.min_history_samples
    ):
        status = RankingStatus.INSUFFICIENT_HISTORY
        adjusted = 0.0
        reasons.append("insufficient_reliability_history")
    else:
        status = RankingStatus.RANKED
        adjusted = provisional

    return ReliabilityAdjustedScore(
        candidate_id=candidate.candidate_id,
        route_id=candidate.route_id,
        status=status,
        raw_edge_bps=candidate.raw_edge_bps,
        bias_penalty_bps=bias_penalty,
        bias_adjusted_edge_bps=bias_adjusted,
        truth_probability=profile.smoothed_truth_rate,
        survival_probability=profile.smoothed_survival_rate,
        history_confidence=profile.history_confidence,
        provisional_score_bps=provisional,
        adjusted_score_bps=adjusted,
        profile=profile,
        reasons=tuple(reasons),
    )


def rank_candidates(
    candidates: Iterable[RankingCandidate],
    observations: list[OpportunityObservation],
    *,
    segment_keys: tuple[str, ...] = ("venue", "regime"),
    policy: ReliabilityPolicy | None = None,
) -> list[ReliabilityAdjustedScore]:
    policy = policy or ReliabilityPolicy()
    scores = [
        score_candidate(
            candidate,
            observations,
            segment_keys=segment_keys,
            policy=policy,
        )
        for candidate in candidates
    ]
    priority = {
        RankingStatus.RANKED: 0,
        RankingStatus.INSUFFICIENT_HISTORY: 1,
        RankingStatus.SUPPRESSED_BY_HISTORY: 2,
        RankingStatus.INELIGIBLE: 3,
    }
    return sorted(
        scores,
        key=lambda score: (
            priority[score.status],
            -score.adjusted_score_bps,
            -score.provisional_score_bps,
            -score.raw_edge_bps,
            score.candidate_id,
        ),
    )
