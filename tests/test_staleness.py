from __future__ import annotations

import pytest

from resonance_arbitrage_graph.quotes import QuoteSnapshot
from resonance_arbitrage_graph.staleness import (
    StalenessPolicy,
    StalenessVerdict,
    assess_quote_staleness,
)


def quote(*, observed_at_ms: int = 1_000, timestamp_class: str = "client_observed",
          source_timestamp_ms: int | None = None) -> QuoteSnapshot:
    return QuoteSnapshot(
        venue="TEST", symbol="BTCUSDT", base_asset="BTC", quote_asset="USDT",
        bid_price=100.0, bid_qty=1.0, ask_price=101.0, ask_qty=1.0,
        observed_at_ms=observed_at_ms, source_url="https://example.invalid/quote",
        timestamp_class=timestamp_class, source_timestamp_ms=source_timestamp_ms,
    )


def test_client_observation_can_be_fresh_when_source_age_is_not_required() -> None:
    result = assess_quote_staleness(
        quote(), now_ms=1_050, policy=StalenessPolicy(max_observation_age_ms=50),
    )
    assert result.verdict is StalenessVerdict.FRESH
    assert result.observation_age_ms == 50
    assert result.source_age_ms is None
    assert "SOURCE_AGE_NOT_REQUIRED" in result.reasons


def test_observation_older_than_bound_is_stale() -> None:
    result = assess_quote_staleness(
        quote(), now_ms=1_051, policy=StalenessPolicy(max_observation_age_ms=50),
    )
    assert result.verdict is StalenessVerdict.STALE
    assert result.reasons == ("CLIENT_OBSERVATION_TOO_OLD",)


def test_binance_style_client_observed_is_unknown_when_source_age_is_required() -> None:
    result = assess_quote_staleness(
        quote(), now_ms=1_010,
        policy=StalenessPolicy(max_observation_age_ms=50, max_source_age_ms=50),
    )
    assert result.verdict is StalenessVerdict.UNKNOWN
    assert result.source_age_ms is None
    assert "SOURCE_PUBLICATION_TIMESTAMP_UNAVAILABLE" in result.reasons


def test_level_update_timestamp_is_not_misused_as_snapshot_publication_time() -> None:
    result = assess_quote_staleness(
        quote(timestamp_class="client_observed_level_update", source_timestamp_ms=900),
        now_ms=1_010,
        policy=StalenessPolicy(max_observation_age_ms=50, max_source_age_ms=50),
    )
    assert result.verdict is StalenessVerdict.UNKNOWN
    assert result.source_age_ms is None
    assert "SOURCE_TIMESTAMP_NOT_SNAPSHOT_PUBLICATION_TIME" in result.reasons


def test_exchange_published_snapshot_within_both_bounds_is_fresh() -> None:
    result = assess_quote_staleness(
        quote(timestamp_class="exchange_published", source_timestamp_ms=980),
        now_ms=1_020,
        policy=StalenessPolicy(max_observation_age_ms=50, max_source_age_ms=40),
    )
    assert result.verdict is StalenessVerdict.FRESH
    assert result.observation_age_ms == 20
    assert result.source_age_ms == 40


def test_exchange_published_snapshot_past_source_bound_is_stale() -> None:
    result = assess_quote_staleness(
        quote(timestamp_class="exchange_published", source_timestamp_ms=979),
        now_ms=1_020,
        policy=StalenessPolicy(max_observation_age_ms=50, max_source_age_ms=40),
    )
    assert result.verdict is StalenessVerdict.STALE
    assert result.source_age_ms == 41
    assert "SOURCE_SNAPSHOT_TOO_OLD" in result.reasons


def test_future_timestamps_are_unknown_not_zero_age() -> None:
    observed_future = assess_quote_staleness(
        quote(observed_at_ms=1_021), now_ms=1_020,
        policy=StalenessPolicy(max_observation_age_ms=50),
    )
    assert observed_future.verdict is StalenessVerdict.UNKNOWN

    source_future = assess_quote_staleness(
        quote(timestamp_class="exchange_published", source_timestamp_ms=1_021),
        now_ms=1_020,
        policy=StalenessPolicy(max_observation_age_ms=50, max_source_age_ms=50),
    )
    assert source_future.verdict is StalenessVerdict.UNKNOWN
    assert "SOURCE_TIMESTAMP_IN_FUTURE" in source_future.reasons


@pytest.mark.parametrize("kwargs", [
    {"max_observation_age_ms": -1},
    {"max_observation_age_ms": True},
    {"max_observation_age_ms": 1, "max_source_age_ms": -1},
    {"max_observation_age_ms": 1, "max_source_age_ms": True},
])
def test_policy_rejects_invalid_bounds(kwargs: dict[str, object]) -> None:
    with pytest.raises(ValueError):
        StalenessPolicy(**kwargs)


def test_now_must_be_non_negative_integer() -> None:
    with pytest.raises(ValueError):
        assess_quote_staleness(
            quote(), now_ms=-1, policy=StalenessPolicy(max_observation_age_ms=50),
        )
