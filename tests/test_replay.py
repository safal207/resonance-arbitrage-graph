from copy import deepcopy
from dataclasses import replace

import pytest

from resonance_arbitrage_graph.engine import Policy
from resonance_arbitrage_graph.observation import OutcomeClass
from resonance_arbitrage_graph.quotes import CostAssumption, QuoteSnapshot
from resonance_arbitrage_graph.regime import MarketRegime, RegimePolicy
from resonance_arbitrage_graph.replay import (
    ReplayBundle,
    ReplayCase,
    ReplayLeg,
    ReplayOutcome,
    ReplaySide,
    benchmark_bundle,
    replay_case,
    threshold_sensitivity,
)
from resonance_arbitrage_graph.rolling_state import RollingMarketWindow, RollingWindowPolicy
from resonance_arbitrage_graph.window_regime import market_key


ZERO = CostAssumption(fee_bps=0.0, slippage_bps=0.0)
WINDOW_POLICY = RollingWindowPolicy(horizon_ms=60_000, min_samples=5, min_coverage_ratio=1.0)


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


def _market_series(symbol: str, base: str, quote: str, mids: list[float], spread: float):
    times = (0, 15_000, 30_000, 45_000, 60_000)
    quotes = tuple(
        _quote(symbol, base, quote, ts, mid, spread)
        for ts, mid in zip(times, mids)
    )
    return quotes, RollingMarketWindow.from_quotes(quotes, policy=WINDOW_POLICY, end_ms=60_000)


def _decision_state():
    btc_series, btc_window = _market_series(
        "BTCUSDT", "BTC", "USDT", [99.99, 100.00, 99.98, 100.01, 99.995], 0.01
    )
    ethbtc_series, ethbtc_window = _market_series(
        "ETHBTC", "ETH", "BTC", [0.49994, 0.49996, 0.49993, 0.49997, 0.49995], 0.0001
    )
    ethusdt_series, ethusdt_window = _market_series(
        "ETHUSDT", "ETH", "USDT", [50.17, 50.18, 50.16, 50.19, 50.185], 0.01
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
    *,
    attempt: int = 1,
    realized_edge_bps: float | None = 40.0,
    expired: bool = False,
    case_id: str | None = None,
) -> ReplayCase:
    snapshots, windows, legs = _decision_state()
    return ReplayCase(
        case_id=case_id or f"{operation}-a{attempt}",
        logical_operation_id=operation,
        attempt=attempt,
        detected_at_ms=60_000,
        evaluation_time_ms=60_000,
        start_amount=1_000.0,
        snapshots=snapshots,
        windows_by_market=windows,
        legs=legs,
        engine_policy=Policy(),
        regime_policy=RegimePolicy(),
        outcome=ReplayOutcome(
            observed_at_ms=61_000 + attempt,
            realized_net_edge_bps=realized_edge_bps,
            expired=expired,
        ),
    )


def test_replay_bundle_round_trip_and_report_are_deterministic():
    bundle = ReplayBundle(cases=(_case("op-tp"), _case("op-fp", realized_edge_bps=10.0)))
    restored = ReplayBundle.from_envelope(deepcopy(bundle.to_envelope()))

    assert restored.sha256 == bundle.sha256
    first = benchmark_bundle(restored)
    second = benchmark_bundle(restored)
    assert first.sha256 == second.sha256
    assert first.canonical_payload() == second.canonical_payload()


def test_replay_recomputes_executable_normal_regime_from_captured_state():
    result = replay_case(_case("op-normal"))

    assert result.expected_verdict.value == "EXECUTE_SIM"
    assert result.expected_edge_bps == pytest.approx(36.0, abs=0.05)
    assert result.regime is MarketRegime.NORMAL
    assert result.outcome_class is OutcomeClass.TRUE_POSITIVE


def test_bundle_tamper_is_detected_before_replay():
    bundle = ReplayBundle(cases=(_case("op-tamper"),))
    envelope = deepcopy(bundle.to_envelope())
    envelope["payload"]["cases"][0]["snapshots"][0]["ask_price"] += 1.0

    with pytest.raises(ValueError, match="SHA-256"):
        ReplayBundle.from_envelope(envelope)


def test_future_market_observation_is_rejected_as_lookahead():
    original = _case("op-future")
    snapshots = list(original.snapshots)
    snapshots[0] = replace(snapshots[0], observed_at_ms=60_001, source_url="fixture:future")

    with pytest.raises(ValueError, match="future quote observation"):
        replace(original, snapshots=tuple(snapshots))


def test_retry_is_collapsed_without_double_counting():
    first = _case("op-retry", attempt=1, realized_edge_bps=None)
    second = _case("op-retry", attempt=2, realized_edge_bps=40.0)
    bundle = ReplayBundle(cases=(first, second))
    report = benchmark_bundle(bundle)

    assert report.overall.logical_operations == 1
    assert report.overall.true_positive == 1
    assert report.results[0].attempt == 2


def test_terminal_attempt_cannot_be_retried():
    first = _case("op-terminal", attempt=1, realized_edge_bps=40.0)
    second = _case("op-terminal", attempt=2, realized_edge_bps=40.0)

    with pytest.raises(ValueError, match="terminal replay outcome"):
        ReplayBundle(cases=(first, second))


def test_logical_retry_cannot_drift_market_decision_state():
    first = _case("op-drift", attempt=1, realized_edge_bps=None)
    second = _case("op-drift", attempt=2, realized_edge_bps=40.0)
    changed = list(second.snapshots)
    changed[2] = replace(changed[2], bid_price=changed[2].bid_price + 0.01)
    second = replace(second, snapshots=tuple(changed))

    with pytest.raises(ValueError, match="drifted"):
        ReplayBundle(cases=(first, second))


def test_incomplete_rolling_evidence_is_indeterminate_not_success():
    case = _case("op-incomplete")
    key = market_key("fixture", "BTCUSDT")
    original = case.windows_by_market[key]
    incomplete = RollingMarketWindow(
        policy=replace(original.policy, min_samples=5, min_coverage_ratio=0.8),
        samples=original.samples[-2:],
    )
    windows = dict(case.windows_by_market)
    windows[key] = incomplete
    case = replace(case, windows_by_market=windows)

    result = replay_case(case)
    assert result.regime is MarketRegime.UNKNOWN
    assert result.outcome_class is OutcomeClass.INDETERMINATE
    assert "REGIME_EVIDENCE_UNKNOWN" in result.reasons


def test_calibration_metrics_are_segmented_by_regime_and_route():
    bundle = ReplayBundle(
        cases=(
            _case("op-tp", realized_edge_bps=40.0),
            _case("op-fp", realized_edge_bps=10.0),
            _case("op-expired", realized_edge_bps=None, expired=True),
        )
    )
    report = benchmark_bundle(bundle)

    assert report.overall.true_positive == 1
    assert report.overall.false_positive == 1
    assert report.overall.expired == 1
    assert report.overall.opportunity_truth_rate == pytest.approx(0.5)
    assert report.overall.route_survival_rate == pytest.approx(2 / 3)
    assert len(report.by_regime) == 1
    assert report.by_regime[0].key == "NORMAL"
    assert len(report.by_route) == 1


def test_threshold_sensitivity_is_advisory_and_changes_prediction_population():
    bundle = ReplayBundle(cases=(_case("op-sensitive", realized_edge_bps=40.0),))
    points = threshold_sensitivity(
        bundle,
        execute_net_edge_bps=[30.0, 50.0],
        volatile_return_bps=[50.0, 75.0],
    )

    assert len(points) == 4
    low = next(point for point in points if point.execute_net_edge_bps == 30.0 and point.volatile_return_bps == 75.0)
    high = next(point for point in points if point.execute_net_edge_bps == 50.0 and point.volatile_return_bps == 75.0)
    assert low.execute_sim_count == 1
    assert high.execute_sim_count == 0
    assert low.to_payload()["advisory_only"] is True
