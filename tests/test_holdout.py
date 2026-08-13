from copy import deepcopy
from dataclasses import replace

import pytest

from resonance_arbitrage_graph.engine import Policy
from resonance_arbitrage_graph.holdout import (
    CandidateGrid,
    HoldoutPolicy,
    HoldoutStatus,
    run_holdout_calibration,
    split_replay_bundle,
    verify_holdout_report_envelope,
    wilson_lower_bound,
)
from resonance_arbitrage_graph.quotes import CostAssumption, QuoteSnapshot
from resonance_arbitrage_graph.regime import RegimePolicy
from resonance_arbitrage_graph.replay import ReplayBundle, ReplayCase, ReplayLeg, ReplayOutcome, ReplaySide
from resonance_arbitrage_graph.rolling_state import RollingMarketWindow, RollingWindowPolicy
from resonance_arbitrage_graph.window_regime import market_key


ZERO = CostAssumption(fee_bps=0.0, slippage_bps=0.0)
WINDOW_POLICY = RollingWindowPolicy(horizon_ms=60_000, min_samples=5, min_coverage_ratio=1.0)
GRID = CandidateGrid(execute_net_edge_bps=(20.0, 40.0), volatile_return_bps=(75.0,))
HOLDOUT_POLICY = HoldoutPolicy(
    validation_fraction=1 / 3,
    min_calibration_operations=4,
    min_validation_operations=2,
    min_calibration_truth_events=3,
    min_validation_truth_events=2,
    min_truth_rate_lower_bound=0.5,
    min_survival_rate_lower_bound=0.5,
    confidence_z=0.0,
)


def _quote(symbol: str, base: str, quote: str, ts: int, mid: float, spread: float) -> QuoteSnapshot:
    return QuoteSnapshot(
        venue="fixture",
        symbol=symbol,
        base_asset=base,
        quote_asset=quote,
        bid_price=mid - spread / 2.0,
        bid_qty=1_000.0,
        ask_price=mid + spread / 2.0,
        ask_qty=1_000.0,
        observed_at_ms=ts,
        source_url=f"fixture:{symbol}:{ts}",
    )


def _market_series(
    symbol: str,
    base: str,
    quote: str,
    end_ms: int,
    mids: list[float],
    spread: float,
):
    times = (
        end_ms - 60_000,
        end_ms - 45_000,
        end_ms - 30_000,
        end_ms - 15_000,
        end_ms,
    )
    quotes = tuple(
        _quote(symbol, base, quote, ts, mid, spread)
        for ts, mid in zip(times, mids)
    )
    return quotes, RollingMarketWindow.from_quotes(
        quotes,
        policy=WINDOW_POLICY,
        end_ms=end_ms,
    )


def _decision_state(end_ms: int):
    btc_series, btc_window = _market_series(
        "BTCUSDT", "BTC", "USDT", end_ms, [99.99, 100.00, 99.98, 100.01, 99.995], 0.01
    )
    ethbtc_series, ethbtc_window = _market_series(
        "ETHBTC", "ETH", "BTC", end_ms, [0.49994, 0.49996, 0.49993, 0.49997, 0.49995], 0.0001
    )
    ethusdt_series, ethusdt_window = _market_series(
        "ETHUSDT", "ETH", "USDT", end_ms, [50.17, 50.18, 50.16, 50.19, 50.185], 0.01
    )
    snapshots = (btc_series[-1], ethbtc_series[-1], ethusdt_series[-1])
    windows = {
        market_key("fixture", "BTCUSDT"): btc_window,
        market_key("fixture", "ETHBTC"): ethbtc_window,
        market_key("fixture", "ETHUSDT"): ethusdt_window,
    }
    legs = (
        ReplayLeg(0, ReplaySide.BUY, ZERO),
        ReplayLeg(1, ReplaySide.BUY, ZERO),
        ReplayLeg(2, ReplaySide.SELL, ZERO),
    )
    return snapshots, windows, legs


def _case(
    operation: str,
    detected_at_ms: int,
    realized_edge_bps: float | None,
    *,
    attempt: int = 1,
    expired: bool = False,
    engine_policy: Policy | None = None,
) -> ReplayCase:
    snapshots, windows, legs = _decision_state(detected_at_ms)
    return ReplayCase(
        case_id=f"{operation}-a{attempt}",
        logical_operation_id=operation,
        attempt=attempt,
        detected_at_ms=detected_at_ms,
        evaluation_time_ms=detected_at_ms,
        start_amount=1_000.0,
        snapshots=snapshots,
        windows_by_market=windows,
        legs=legs,
        engine_policy=engine_policy or Policy(),
        regime_policy=RegimePolicy(),
        outcome=ReplayOutcome(
            observed_at_ms=detected_at_ms + 1_000 + attempt,
            realized_net_edge_bps=realized_edge_bps,
            expired=expired,
        ),
    )


def _bundle(validation_outcomes=(40.0, 40.0)) -> ReplayBundle:
    calibration = (40.0, 40.0, 40.0, 10.0)
    outcomes = calibration + tuple(validation_outcomes)
    return ReplayBundle(
        cases=tuple(
            _case(f"op-{index + 1}", 60_000 * (index + 1), outcome)
            for index, outcome in enumerate(outcomes)
        )
    )


def test_chronological_split_keeps_retries_together_and_validation_later():
    cases = [
        _case("op-1", 60_000, None, attempt=1),
        _case("op-1", 60_000, 40.0, attempt=2),
    ]
    cases.extend(
        _case(f"op-{index}", 60_000 * index, 40.0)
        for index in range(2, 7)
    )
    split = split_replay_bundle(ReplayBundle(cases=tuple(cases)), HOLDOUT_POLICY)

    calibration_ids = {case.logical_operation_id for case in split.calibration.cases}
    validation_ids = {case.logical_operation_id for case in split.validation.cases}
    assert "op-1" in calibration_ids
    assert sum(case.logical_operation_id == "op-1" for case in split.calibration.cases) == 2
    assert not calibration_ids & validation_ids
    assert split.summary.calibration_max_detected_at_ms < split.summary.validation_min_detected_at_ms
    assert len(split.calibration.collapsed_cases()) == 4
    assert len(split.validation.collapsed_cases()) == 2


def test_holdout_selects_on_calibration_and_passes_out_of_sample_validation():
    report = run_holdout_calibration(_bundle(), GRID, HOLDOUT_POLICY)

    assert report.status is HoldoutStatus.PASSED_HOLDOUT
    assert report.selected_candidate is not None
    assert report.selected_candidate.execute_net_edge_bps == 20.0
    assert report.validation_evaluation is not None
    assert report.validation_evaluation.eligible is True
    assert report.canonical_payload()["validation_not_used_for_selection"] is True
    assert report.sha256 == run_holdout_calibration(_bundle(), GRID, HOLDOUT_POLICY).sha256


def test_validation_outcomes_cannot_change_selected_calibration_candidate():
    passing = run_holdout_calibration(_bundle((40.0, 40.0)), GRID, HOLDOUT_POLICY)
    failing = run_holdout_calibration(_bundle((10.0, 10.0)), GRID, HOLDOUT_POLICY)

    assert passing.selected_candidate == failing.selected_candidate
    assert [item.to_payload() for item in passing.calibration_evaluations] == [
        item.to_payload() for item in failing.calibration_evaluations
    ]
    assert passing.status is HoldoutStatus.PASSED_HOLDOUT
    assert failing.status is HoldoutStatus.VALIDATION_FAILED
    assert failing.selected_candidate is not None
    assert failing.selected_candidate.execute_net_edge_bps == 20.0


def test_insufficient_validation_truth_support_fails_closed():
    report = run_holdout_calibration(_bundle((None, None)), GRID, HOLDOUT_POLICY)

    assert report.status is HoldoutStatus.INSUFFICIENT_VALIDATION
    assert report.selected_candidate is not None
    assert report.validation_evaluation is not None
    assert report.validation_evaluation.truth_events == 0


def test_insufficient_corpus_returns_explicit_status():
    bundle = ReplayBundle(
        cases=tuple(
            _case(f"op-{index + 1}", 60_000 * (index + 1), 40.0)
            for index in range(5)
        )
    )
    report = run_holdout_calibration(bundle, GRID, HOLDOUT_POLICY)

    assert report.status is HoldoutStatus.INSUFFICIENT_CORPUS
    assert report.split is None
    assert report.selected_candidate is None


def test_no_strict_chronological_boundary_fails_closed():
    bundle = ReplayBundle(
        cases=tuple(_case(f"op-{index + 1}", 60_000, 40.0) for index in range(6))
    )
    report = run_holdout_calibration(bundle, GRID, HOLDOUT_POLICY)

    assert report.status is HoldoutStatus.INSUFFICIENT_CORPUS
    assert "strict chronological boundary" in report.reasons[0]


def test_untuned_policy_context_drift_is_rejected():
    bundle = _bundle()
    cases = list(bundle.cases)
    cases[-1] = replace(
        cases[-1],
        engine_policy=replace(cases[-1].engine_policy, max_quote_age_ms=4_000),
    )

    with pytest.raises(ValueError, match="policy context drifted"):
        run_holdout_calibration(ReplayBundle(cases=tuple(cases)), GRID, HOLDOUT_POLICY)


def test_candidate_execute_threshold_must_exceed_corpus_observe_threshold():
    base_policy = Policy(execute_net_edge=0.004, observe_net_edge=0.003)
    bundle = ReplayBundle(
        cases=tuple(
            _case(
                f"op-{index + 1}",
                60_000 * (index + 1),
                40.0,
                engine_policy=base_policy,
            )
            for index in range(6)
        )
    )

    with pytest.raises(ValueError, match="must exceed the corpus observe threshold"):
        run_holdout_calibration(bundle, GRID, HOLDOUT_POLICY)


def test_holdout_report_envelope_detects_tamper():
    report = run_holdout_calibration(_bundle(), GRID, HOLDOUT_POLICY)
    envelope = deepcopy(report.to_envelope())
    envelope["payload"]["selected_candidate"]["execute_net_edge_bps"] += 1.0

    with pytest.raises(ValueError, match="SHA-256"):
        verify_holdout_report_envelope(envelope)


def test_wilson_lower_bound_is_uncertainty_sensitive():
    assert wilson_lower_bound(1, 1, z=1.96) < wilson_lower_bound(10, 10, z=1.96)
    assert wilson_lower_bound(3, 4, z=0.0) == pytest.approx(0.75)
    assert wilson_lower_bound(0, 0, z=1.96) is None
