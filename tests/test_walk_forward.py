from copy import deepcopy
from dataclasses import replace
import hashlib
import json

import pytest

from resonance_arbitrage_graph.engine import Policy
from resonance_arbitrage_graph.holdout import HoldoutPolicy
from resonance_arbitrage_graph.joint_holdout import JointCandidateGrid, JointHoldoutPolicy, JointPolicyCandidate
from resonance_arbitrage_graph.quotes import CostAssumption, QuoteSnapshot
from resonance_arbitrage_graph.regime import RegimePolicy
from resonance_arbitrage_graph.regime_gate import RegimeExecutionPolicy
from resonance_arbitrage_graph.replay import ReplayBundle, ReplayCase, ReplayLeg, ReplayOutcome, ReplaySide
from resonance_arbitrage_graph.rolling_state import RollingMarketWindow, RollingWindowPolicy
from resonance_arbitrage_graph.walk_forward import (
    WalkForwardPolicy,
    WalkForwardStatus,
    _candidate_switch_metrics,
    plan_walk_forward_folds,
    run_walk_forward_stability,
    verify_walk_forward_report_bundle_binding,
    verify_walk_forward_report_envelope,
)
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
        bid_qty=10_000.0,
        ask_price=mid + spread / 2.0,
        ask_qty=10_000.0,
        observed_at_ms=ts,
        source_url=f"fixture:{symbol}:{ts}",
    )


def _series(
    symbol: str,
    base: str,
    quote: str,
    times: tuple[int, ...],
    mids: tuple[float, ...],
    spread: float,
):
    quotes = tuple(
        _quote(symbol, base, quote, ts, mid, spread)
        for ts, mid in zip(times, mids)
    )
    return quotes, RollingMarketWindow.from_quotes(
        quotes,
        policy=WINDOW_POLICY,
        end_ms=times[-1],
    )


def _btc_mids(volatility: str) -> tuple[float, ...]:
    if volatility == "low":
        return (99.99, 100.00, 99.98, 100.01, 99.995)
    if volatility == "medium":
        return (100.00, 100.25, 99.95, 100.20, 99.995)
    raise ValueError("unknown volatility fixture")


def _decision_state(offset: int, *, volatility: str, edge_bps: float):
    times = tuple(offset + value for value in (0, 15_000, 30_000, 45_000, 60_000))
    btc_series, btc_window = _series(
        "BTCUSDT", "BTC", "USDT", times, _btc_mids(volatility), 0.01
    )
    ethbtc_series, ethbtc_window = _series(
        "ETHBTC",
        "ETH",
        "BTC",
        times,
        (0.49994, 0.49996, 0.49993, 0.49997, 0.49995),
        0.0001,
    )
    target_bid = 50.0 * (1.0 + edge_bps / 10_000.0)
    target_mid = target_bid + 0.005
    ethusdt_series, ethusdt_window = _series(
        "ETHUSDT",
        "ETH",
        "USDT",
        times,
        (
            target_mid - 0.005,
            target_mid,
            target_mid - 0.01,
            target_mid + 0.005,
            target_mid,
        ),
        0.01,
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
    return times[-1], snapshots, windows, legs


def _case(
    operation: str,
    order: int,
    *,
    volatility: str,
    edge_bps: float,
    realized_edge_bps: float | None,
    outcome_delay_ms: int = 1_000,
) -> ReplayCase:
    evaluation_time, snapshots, windows, legs = _decision_state(
        order * 100_000,
        volatility=volatility,
        edge_bps=edge_bps,
    )
    return ReplayCase(
        case_id=f"{operation}-a1",
        logical_operation_id=operation,
        attempt=1,
        detected_at_ms=evaluation_time,
        evaluation_time_ms=evaluation_time,
        start_amount=1_000.0,
        snapshots=snapshots,
        windows_by_market=windows,
        legs=legs,
        engine_policy=Policy(),
        regime_policy=RegimePolicy(volatile_return_bps=75.0),
        regime_execution_policy=RegimeExecutionPolicy(),
        outcome=ReplayOutcome(
            observed_at_ms=evaluation_time + outcome_delay_ms,
            realized_net_edge_bps=realized_edge_bps,
        ),
    )


def _triad(prefix: str, start_order: int, *, truth_edge: float = 39.0) -> tuple[ReplayCase, ...]:
    return (
        _case(
            f"{prefix}-execute",
            start_order,
            volatility="low",
            edge_bps=32.0,
            realized_edge_bps=32.0,
        ),
        _case(
            f"{prefix}-volatility",
            start_order + 1,
            volatility="medium",
            edge_bps=39.0,
            realized_edge_bps=39.0,
        ),
        _case(
            f"{prefix}-truth",
            start_order + 2,
            volatility="low",
            edge_bps=39.0,
            realized_edge_bps=truth_edge,
        ),
    )


def _bundle(*, bad_validation_truth: bool = False) -> ReplayBundle:
    cases: list[ReplayCase] = []
    cases.extend(_triad("cal", 1))
    cases.extend(_triad("val1", 4))
    cases.extend(_triad("val2", 7, truth_edge=5.0 if bad_validation_truth else 39.0))
    cases.extend(_triad("val3", 10))
    return ReplayBundle(cases=tuple(cases))


def _policy(
    *,
    min_pass_rate: float = 1.0,
    max_switch_rate: float = 0.0,
) -> WalkForwardPolicy:
    holdout = HoldoutPolicy(
        validation_fraction=0.5,
        min_calibration_operations=3,
        min_validation_operations=3,
        min_calibration_truth_events=1,
        min_validation_truth_events=1,
        min_truth_rate_lower_bound=1.0,
        min_survival_rate_lower_bound=1.0,
        confidence_z=0.0,
    )
    joint = JointHoldoutPolicy(
        holdout=holdout,
        min_calibration_execute_causal_changes=1,
        min_calibration_volatility_causal_changes=1,
        min_validation_execute_causal_changes=1,
        min_validation_volatility_causal_changes=1,
    )
    return WalkForwardPolicy(
        joint_policy=joint,
        initial_calibration_operations=3,
        validation_operations=3,
        min_folds=3,
        min_selected_policy_folds=3,
        min_validation_pass_rate=min_pass_rate,
        max_policy_switch_rate=max_switch_rate,
    )


def _grid() -> JointCandidateGrid:
    return JointCandidateGrid(
        execute_net_edge_bps=(35.0,),
        volatile_return_bps=(20.0,),
    )


def _canonical_sha(payload: dict) -> str:
    raw = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def test_walk_forward_passes_three_strict_temporal_folds():
    bundle = _bundle()
    report = run_walk_forward_stability(bundle, _grid(), _policy())

    assert report.status is WalkForwardStatus.PASSED_STABILITY
    assert report.metrics.total_folds == 3
    assert report.metrics.passed_folds == 3
    assert report.metrics.validation_pass_rate == 1.0
    assert report.metrics.selected_policy_folds == 3
    assert report.metrics.policy_switches == 0
    assert report.metrics.policy_switch_rate == 0.0
    assert report.plan.unused_tail_operation_ids == ()
    assert verify_walk_forward_report_bundle_binding(report, bundle) is True


def test_outcome_availability_firewall_moves_first_boundary_forward():
    bundle = _bundle()
    delayed = replace(
        bundle.cases[0],
        outcome=ReplayOutcome(
            observed_at_ms=bundle.cases[3].detected_at_ms + 1,
            realized_net_edge_bps=32.0,
        ),
    )
    bundle = ReplayBundle(cases=(delayed,) + bundle.cases[1:])

    plan = plan_walk_forward_folds(bundle, _policy())

    assert plan.folds
    first = plan.folds[0]
    assert len(first.calibration_operation_ids) == 4
    assert first.calibration_max_observed_at_ms < first.validation_min_detected_at_ms


def test_validation_failures_are_counted_not_dropped():
    report = run_walk_forward_stability(
        _bundle(bad_validation_truth=True),
        _grid(),
        _policy(min_pass_rate=1.0),
    )

    assert report.status is WalkForwardStatus.UNSTABLE
    assert report.metrics.total_folds == 3
    assert report.metrics.failed_folds >= 1
    assert report.metrics.validation_pass_rate < 1.0
    assert "VALIDATION_PASS_RATE_BELOW_FLOOR" in report.reasons


def test_candidate_switch_metric_detects_temporal_policy_drift():
    a = JointPolicyCandidate(execute_net_edge_bps=35.0, volatile_return_bps=20.0)
    b = JointPolicyCandidate(execute_net_edge_bps=40.0, volatile_return_bps=40.0)

    unique, switches, switch_rate, min_execute, max_execute, min_vol, max_vol = (
        _candidate_switch_metrics((a, a, b, a))
    )

    assert unique == 2
    assert switches == 2
    assert switch_rate == pytest.approx(2.0 / 3.0)
    assert (min_execute, max_execute) == (35.0, 40.0)
    assert (min_vol, max_vol) == (20.0, 40.0)


def test_walk_forward_report_rejects_forged_outcome_availability_even_with_new_outer_sha():
    report = run_walk_forward_stability(_bundle(), _grid(), _policy())
    envelope = deepcopy(report.to_envelope())
    fold_plan = envelope["payload"]["plan"]["folds"][0]
    fold_plan["calibration_max_observed_at_ms"] = fold_plan["validation_min_detected_at_ms"]
    envelope["payload"]["folds"][0]["plan"] = deepcopy(fold_plan)
    envelope["sha256"] = _canonical_sha(envelope["payload"])

    with pytest.raises(ValueError, match="outcome-availability"):
        verify_walk_forward_report_envelope(envelope)


def test_walk_forward_report_is_deterministic():
    first = run_walk_forward_stability(_bundle(), _grid(), _policy())
    second = run_walk_forward_stability(_bundle(), _grid(), _policy())

    assert first.sha256 == second.sha256
    assert first.canonical_payload() == second.canonical_payload()
    assert verify_walk_forward_report_envelope(first.to_envelope()) == first.canonical_payload()
