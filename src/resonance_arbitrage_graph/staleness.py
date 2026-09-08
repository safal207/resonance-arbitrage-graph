"""Bounded quote-staleness assessment with explicit evidence limits."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .quotes import QuoteSnapshot


class StalenessVerdict(str, Enum):
    FRESH = "FRESH"
    STALE = "STALE"
    UNKNOWN = "UNKNOWN"


def _non_negative_int(name: str, value: int | None, *, optional: bool = False) -> None:
    if optional and value is None:
        return
    if type(value) is not int or value < 0:
        suffix = " or None" if optional else ""
        raise ValueError(f"{name} must be a non-negative integer{suffix}")


@dataclass(frozen=True, slots=True)
class StalenessPolicy:
    """Caller-supplied limits; not trading recommendations or venue guarantees.

    ``max_observation_age_ms`` bounds how old the local observation may be.
    ``max_source_age_ms`` additionally requires a timestamp that represents
    publication time of the complete snapshot. If that evidence is unavailable,
    the assessment is UNKNOWN rather than treating local receipt time as source age.
    """

    max_observation_age_ms: int
    max_source_age_ms: int | None = None

    def __post_init__(self) -> None:
        _non_negative_int("max_observation_age_ms", self.max_observation_age_ms)
        _non_negative_int("max_source_age_ms", self.max_source_age_ms, optional=True)


@dataclass(frozen=True, slots=True)
class StalenessAssessment:
    verdict: StalenessVerdict
    observation_age_ms: int | None
    source_age_ms: int | None
    reasons: tuple[str, ...]
    timestamp_class: str
    max_observation_age_ms: int
    max_source_age_ms: int | None


def assess_quote_staleness(
    quote: QuoteSnapshot,
    *,
    now_ms: int,
    policy: StalenessPolicy,
) -> StalenessAssessment:
    """Assess only what the timestamp semantics can prove.

    ``client_observed_level_update`` timestamps are intentionally not used as
    full-snapshot publication timestamps. Future timestamps produce UNKNOWN
    instead of being clamped to zero age.
    """

    _non_negative_int("now_ms", now_ms)

    if quote.observed_at_ms > now_ms:
        return StalenessAssessment(
            verdict=StalenessVerdict.UNKNOWN,
            observation_age_ms=None,
            source_age_ms=None,
            reasons=("CLIENT_OBSERVED_TIMESTAMP_IN_FUTURE",),
            timestamp_class=quote.timestamp_class,
            max_observation_age_ms=policy.max_observation_age_ms,
            max_source_age_ms=policy.max_source_age_ms,
        )

    observation_age_ms = now_ms - quote.observed_at_ms
    if observation_age_ms > policy.max_observation_age_ms:
        return StalenessAssessment(
            verdict=StalenessVerdict.STALE,
            observation_age_ms=observation_age_ms,
            source_age_ms=None,
            reasons=("CLIENT_OBSERVATION_TOO_OLD",),
            timestamp_class=quote.timestamp_class,
            max_observation_age_ms=policy.max_observation_age_ms,
            max_source_age_ms=policy.max_source_age_ms,
        )

    if policy.max_source_age_ms is None:
        return StalenessAssessment(
            verdict=StalenessVerdict.FRESH,
            observation_age_ms=observation_age_ms,
            source_age_ms=None,
            reasons=("CLIENT_OBSERVATION_WITHIN_BOUND", "SOURCE_AGE_NOT_REQUIRED"),
            timestamp_class=quote.timestamp_class,
            max_observation_age_ms=policy.max_observation_age_ms,
            max_source_age_ms=None,
        )

    if quote.timestamp_class != "exchange_published":
        reason = (
            "SOURCE_TIMESTAMP_NOT_SNAPSHOT_PUBLICATION_TIME"
            if quote.timestamp_class == "client_observed_level_update"
            else "SOURCE_PUBLICATION_TIMESTAMP_UNAVAILABLE"
        )
        return StalenessAssessment(
            verdict=StalenessVerdict.UNKNOWN,
            observation_age_ms=observation_age_ms,
            source_age_ms=None,
            reasons=("CLIENT_OBSERVATION_WITHIN_BOUND", reason),
            timestamp_class=quote.timestamp_class,
            max_observation_age_ms=policy.max_observation_age_ms,
            max_source_age_ms=policy.max_source_age_ms,
        )

    assert quote.source_timestamp_ms is not None
    if quote.source_timestamp_ms > now_ms:
        return StalenessAssessment(
            verdict=StalenessVerdict.UNKNOWN,
            observation_age_ms=observation_age_ms,
            source_age_ms=None,
            reasons=("CLIENT_OBSERVATION_WITHIN_BOUND", "SOURCE_TIMESTAMP_IN_FUTURE"),
            timestamp_class=quote.timestamp_class,
            max_observation_age_ms=policy.max_observation_age_ms,
            max_source_age_ms=policy.max_source_age_ms,
        )

    source_age_ms = now_ms - quote.source_timestamp_ms
    if source_age_ms > policy.max_source_age_ms:
        return StalenessAssessment(
            verdict=StalenessVerdict.STALE,
            observation_age_ms=observation_age_ms,
            source_age_ms=source_age_ms,
            reasons=("CLIENT_OBSERVATION_WITHIN_BOUND", "SOURCE_SNAPSHOT_TOO_OLD"),
            timestamp_class=quote.timestamp_class,
            max_observation_age_ms=policy.max_observation_age_ms,
            max_source_age_ms=policy.max_source_age_ms,
        )

    return StalenessAssessment(
        verdict=StalenessVerdict.FRESH,
        observation_age_ms=observation_age_ms,
        source_age_ms=source_age_ms,
        reasons=("CLIENT_OBSERVATION_WITHIN_BOUND", "SOURCE_SNAPSHOT_WITHIN_BOUND"),
        timestamp_class=quote.timestamp_class,
        max_observation_age_ms=policy.max_observation_age_ms,
        max_source_age_ms=policy.max_source_age_ms,
    )
