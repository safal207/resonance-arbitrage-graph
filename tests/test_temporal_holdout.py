from dataclasses import replace
from datetime import timedelta

import pytest

from resonance_arbitrage_graph.temporal_holdout import (
    ASSETS, DIRECTIONS, START, DAYS, HoldoutObservation,
    _sign_test, assess_observations, main,
)


def _sample(*, days=DAYS, pos16=4, pos01=1):
    observations = []
    pairs = [(asset, direction) for asset in ASSETS for direction in DIRECTIONS]
    for day_index in range(days):
        day = START + timedelta(days=day_index)
        for hour, npositive in ((1, pos01), (16, pos16)):
            for index, (asset, direction) in enumerate(pairs):
                observations.append(
                    HoldoutObservation(
                        date_utc=day,
                        hour_utc=hour,
                        asset=asset,
                        direction=direction,
                        gross_positive=index < npositive,
                    )
                )
    return observations


def test_exact_sign_test_respects_ties():
    assert _sign_test(0, 0) == 1
    assert _sign_test(28, 0) == pytest.approx(2 / 2 ** 28)
    assert _sign_test(10, 10) == 1


def test_complete_future_sample_can_replicate_prespecified_gross_pattern():
    result = assess_observations(_sample())
    assert result["status"] == "REPLICATED_GROSS_PATTERN"
    assert result["all_observations"] == 560
    assert result["complete_paired_days"] == 28
    assert result["paired_cycles_per_arm"] == 280
    assert result["gross_positive_16"] == 112
    assert result["gross_positive_01"] == 28
    assert result["difference_16_minus_01"] == pytest.approx(.3)
    assert result["paired_day_wins_16"] == 28
    assert result["paired_day_two_sided_sign_p"] < .05


def test_flat_sample_does_not_replicate():
    result = assess_observations(_sample(pos16=2, pos01=2))
    assert result["status"] == "NOT_REPLICATED"
    assert result["difference_16_minus_01"] == 0
    assert result["paired_day_ties"] == 28
    assert result["paired_day_two_sided_sign_p"] == 1


def test_incomplete_sample_is_inconclusive_even_with_large_effect():
    result = assess_observations(_sample(days=23))
    assert result["status"] == "INCONCLUSIVE_COVERAGE"
    assert result["complete_paired_days"] == 23
    assert len(result["incomplete_paired_days"]) == 5
    assert len(result["daily"]) == 28


def test_single_missing_route_invalidates_pair_not_silently_renormalized():
    rows = _sample()
    day = START
    omitted = [
        x for x in rows
        if not (x.date_utc == day and x.hour_utc == 16
                and x.asset == "ETH" and x.direction == "via_BTC")
    ]
    result = assess_observations(omitted)
    assert result["complete_paired_days"] == 27
    assert result["daily"][0]["observed_16"] == 9
    assert result["daily"][0]["complete_pair"] is False


@pytest.mark.parametrize("change", [
    lambda x: replace(x, date_utc=START - timedelta(days=1)),
    lambda x: replace(x, hour_utc=15),
    lambda x: replace(x, asset="DOGE"),
    lambda x: replace(x, direction="reversed"),
    lambda x: replace(x, gross_positive=1),
    lambda x: replace(x, net_positive=True, gross_positive=False),
])
def test_invalid_or_unregistered_record_fails_closed(change):
    row = _sample(days=1)[0]
    with pytest.raises(ValueError):
        assess_observations([change(row)])


def test_duplicate_route_on_same_slot_fails_closed():
    row = _sample(days=1)[0]
    with pytest.raises(ValueError, match="duplicate"):
        assess_observations([row, row])


def test_missing_future_corpus_cannot_fall_back_to_historical(tmp_path):
    with pytest.raises(SystemExit):
        main([str(tmp_path / "nonexistent-holdout.json"),
              "--output", str(tmp_path / "result.json")])
