from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from resonance_arbitrage_graph.campaign003_collection_gate import (
    LAST_START_MINUTE,
    MAX_OPERATIONS,
    START_MINUTE,
    classify_capture,
)
from resonance_arbitrage_graph.temporal_holdout import START, DAYS, SLOTS_UTC

UTC = timezone.utc


def instant(day=1, hour=1, minute=17, year=2026, month=12):
    return datetime(year, month, day, hour, minute, tzinfo=UTC)


def epoch_ms(value):
    return int(value.timestamp() * 1000)


def test_valid_day_and_hour_are_eligible_before_first_observation():
    got = classify_capture(now_utc=instant(), existing_decision_times_ms=())
    assert got.status == "ELIGIBLE"
    assert got.may_collect
    assert got.previous_cases == 0
    assert (START_MINUTE, LAST_START_MINUTE) == (12, 30)


@pytest.mark.parametrize("now", [
    instant(month=11, day=30), instant(day=29), instant(year=2027),
    instant(hour=6), instant(minute=11), instant(minute=31),
])
def test_non_preregistered_time_never_collects(now):
    decision = classify_capture(now_utc=now, existing_decision_times_ms=())
    assert not decision.may_collect


def test_second_attempt_in_same_slot_is_rejected_even_when_partial():
    t = instant(minute=17)
    got = classify_capture(
        now_utc=instant(minute=18),
        existing_decision_times_ms=(epoch_ms(t),),
    )
    assert got.status == "ALREADY_STARTED"


def test_a_previous_valid_slot_does_not_block_a_new_slot():
    t = instant(hour=1)
    got = classify_capture(
        now_utc=instant(hour=16),
        existing_decision_times_ms=(epoch_ms(t),) * 10,
    )
    assert got.status == "ELIGIBLE"


def test_reject_changed_dates_and_future_poisoned_records():
    with pytest.raises(ValueError, match="off-window"):
        classify_capture(
            now_utc=instant(),
            existing_decision_times_ms=(epoch_ms(instant(month=9, day=21)),),
        )
    with pytest.raises(ValueError, match="future"):
        classify_capture(
            now_utc=instant(minute=17),
            existing_decision_times_ms=(epoch_ms(instant(minute=25)),),
        )


def test_strict_limit_rejects_overfilled_slot():
    timestamps = tuple(epoch_ms(instant(minute=15)) for _ in range(11))
    with pytest.raises(ValueError, match="ten-case ceiling"):
        classify_capture(now_utc=instant(minute=20), existing_decision_times_ms=timestamps)


def test_budget_exhaustion_only_after_planned_560():
    prior = []
    for day in range(DAYS):
        for hour in SLOTS_UTC:
            mark = datetime(START.year, START.month, START.day,
                            hour, 15, tzinfo=UTC) + timedelta(days=day)
            prior.extend([epoch_ms(mark)] * 10)
    assert len(prior) == MAX_OPERATIONS == 560
    decision = classify_capture(
        now_utc=instant(day=28, hour=16, minute=19),
        existing_decision_times_ms=tuple(prior),
    )
    assert decision.status == "BUDGET_EXHAUSTED"
    assert not decision.may_collect


def test_timezone_aware_input_converts_to_utc():
    gazipasa = timezone(timedelta(hours=3))
    local_time = datetime(2026, 12, 1, 4, 17, tzinfo=gazipasa)
    assert classify_capture(
        now_utc=local_time, existing_decision_times_ms=()
    ).status == "ELIGIBLE"


def test_naive_datetime_fails_closed():
    with pytest.raises(ValueError, match="timezone-aware"):
        classify_capture(
            now_utc=datetime(2026, 12, 1, 1, 17),
            existing_decision_times_ms=(),
        )


def test_workflow_never_collects_from_push_or_manual_dispatch():
    yaml = Path(".github/workflows/campaign-003-collector.yml").read_text()
    assert "if: github.event_name == 'schedule'" in yaml
    assert 'cron: "17 1,16 1-28 12 *"' in yaml
    assert "data/corpus-campaign-003" in yaml
    assert "data/corpus-campaign-002" not in yaml
    assert "ref: ${{ github.sha }}" in yaml
    assert "cancel-in-progress: false" in yaml
    assert "--campaign-id corpus-campaign-003" in yaml
    assert "--amount 25" in yaml
    assert "--fee-bps 10" in yaml
    assert "--slippage-bps 2" in yaml
    assert "--execute-net-edge-bps 5" in yaml
    assert "--max-route-latency-ms 5000" in yaml
    assert "--min-success-probability 0.75" in yaml
    assert "--max-cases 2" in yaml
    assert "Never force-push" in yaml
    assert "No collection is performed by push or manual dispatch" in yaml
    assert "if: always() && steps.gate.outputs.collect == 'true'" in yaml
    assert "git push origin HEAD:data/corpus-campaign-003" in yaml


def test_future_collector_pins_code_and_does_not_change_source_mid_campaign():
    yaml = Path(".github/workflows/campaign-003-collector.yml").read_text()
    assert "Pin acquisition code SHA before first capture" in yaml
    assert 'collector-source-sha.txt' in yaml
    assert "Collector code SHA drift detected" in yaml
    assert yaml.index("Pin acquisition code SHA before first capture") < yaml.index(
        "Capture exactly one attempt per frozen market profile"
    )


def test_preregistered_evaluator_checks_other_frozen_policy_guards():
    from inspect import getsource
    from resonance_arbitrage_graph.temporal_holdout import extract_holdout

    src = getsource(extract_holdout)
    assert "case.engine_policy.max_route_latency_ms != 5000" in src
    assert "case.engine_policy.min_success_probability - 0.75" in src
    assert "case.engine_policy.observe_net_edge - 0.0" in src


def test_collector_checks_out_pinned_code_before_installing_and_sampling():
    yaml = Path(".github/workflows/campaign-003-collector.yml").read_text()
    assert "Restore frozen collector code after initial slot" in yaml
    assert 'git -C "$code" cat-file -e "$pinned^{commit}"' in yaml
    assert 'git -C "$code" fetch --no-tags --depth=1 origin "$pinned"' in yaml
    assert 'git -C "$code" checkout --detach "$pinned"' in yaml
    assert 'if [[ ! "$pinned" =~ ^[0-9a-f]{40}$ ]]' in yaml
    assert yaml.index("Restore frozen collector code after initial slot") < yaml.index(
        "Install paper-only scanner"
    )
    assert yaml.index("Install paper-only scanner") < yaml.index(
        "Check strict UTC window, canonical corpus and prior slots"
    )
    assert yaml.index("Check strict UTC window, canonical corpus and prior slots") < yaml.index(
        "Pin acquisition code SHA before first capture"
    )
