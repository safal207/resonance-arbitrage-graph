from copy import deepcopy
from dataclasses import replace

import pytest

from resonance_arbitrage_graph.engine import Policy
from resonance_arbitrage_graph.holdout import HoldoutPolicy
from resonance_arbitrage_graph.joint_holdout import (
    JointCandidateGrid,
    JointHoldoutPolicy,
    JointHoldoutStatus,
    JointPolicyCandidate,
    evaluate_joint_policy_candidate,
    run_joint_holdout_calibration,
    validate_joint_policy_context,
    verify_joint_holdout_report_envelope,
)
from resonance_arbitrage_graph.quotes import CostAssumption, QuoteSnapshot
from resonance_arbitrage_graph.regime import RegimePolicy
from resonance_arbitrage_graph.regime_gate import RegimeAction, RegimeExecutionPolicy
from resonance_arbitrage_graph.replay import ReplayBundle, ReplayCase, ReplayLeg, ReplayOutcome, ReplaySide
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
    if volatility == "high":
        return (100.00, 100.45, 99.85, 100.40, 99.995)
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
            observed_at_ms=evaluation_time + 1_000,
            realized_net_edge_bps=realized_edge_bps,
        ),
    )


def _joint_policy(*, validation_execute: int = 1, validation_volatility: int = 1) -> JointHoldoutPolicy:
    return JointHoldoutPolicy(
        holdout=HoldoutPolicy(
            validation_fraction=0.30,
            min_calibration_operations=4,
            min_validation_operations=3,
            min_calibration_truth_events=1,
            min_validation_truth_events=1,
            min_truth_rate_lower_bound=0.0,
            min_survival_rate_lower_bound=0.0,
            confidence_z=0.0,
        ),
        min_calibration_execute_causal_changes=1,
        min_calibration_volatility_causal_changes=1,
        min_validation_execute_causal_changes=validation_execute,
        min_validation_volatility_causal_changes=validation_volatility,
    )


def _support_bundle() -> ReplayBundle:
    return ReplayBundle(
        cases=(
            _case("op-execute", 1, volatility="low", edge_bps=32.0, realized_edge_bps=32.0),
            _case("op-volatility", 2, volatility="medium", edge_bps=39.0, realized_edge_bps=39.0),
            _case("op-truth", 3, volatility="low", edge_bps=39.0, realized_edge_bps=39.0),
        )
    )


def _holdout_bundle(*, validation_flip: bool = False) -> ReplayBundle:
    validation_truth = 5.0 if validation_flip else 39.0
    validation_medium = 39.0 if validation_flip else 5.0
    return ReplayBundle(
        cases=(
            _case("cal-low-tp", 1, volatility="low", edge_bps=39.0, realized_edge_bps=39.0),
            _case("cal-medium-fp", 2, volatility="medium", edge_bps=36.0, realized_edge_bps=5.0),
            _case("cal-high-fp", 3, volatility="high", edge_bps=39.0, realized_edge_bps=5.0),
            _case("cal-execute-support", 4, volatility="low", edge_bps=32.0, realized_edge_bps=32.0),
            _case("val-execute-support", 5, volatility="low", edge_bps=32.0, realized_edge_bps=32.0),
            _case("val-volatility-support", 6, volatility="medium", edge_bps=39.0, realized_edge_bps=validation_medium),
            _case("val-truth", 7, volatility="low", edge_bps=39.0, realized_edge_bps=validation_truth),
        )
    )


def test_joint_candidate_requires_final_verdict_volatility_support():
    bundle = _support_bundle()
    context = validate_joint_policy_context(bundle)
    policy = JointHoldoutPolicy(
        holdout=replace(
            _joint_policy().holdout,
            min_calibration_operations=1,
            min_validation_operations=1,
        ),
        min_calibration_execute_causal_changes=1,
        min_calibration_volatility_causal_changes=1,
        min_validation_execute_causal_changes=0,
        min_validation_volatility_causal_changes=0,
    )
    candidate = JointPolicyCandidate(execute_net_edge_bps=35.0, volatile_return_bps=20.0)

    evaluation = evaluate_joint_policy_candidate(
        bundle,
        candidate,
        policy,
        context,
        min_truth_events=1,
        min_execute_causal_changes=1,
        min_volatility_causal_changes=1,
    )

    assert evaluation.causal_support.execute_final_verdict_changes >= 1
    assert evaluation.causal_support.volatility_regime_label_changes >= 1
    assert evaluation.causal_support.volatility_final_verdict_changes >= 1
    assert evaluation.eligible is True


def test_regime_label_change_without_final_verdict_change_is_not_causal_support():
    bundle = ReplayBundle(
        cases=(
            _case("label-only", 1, volatility="medium", edge_bps=32.0, realized_edge_bps=32.0),
        )
    )
    context = validate_joint_policy_context(bundle)
    policy = JointHoldoutPolicy(
        holdout=HoldoutPolicy(
            validation_fraction=0.5,
            min_calibration_operations=1,
            min_validation_operations=1,
            min_calibration_truth_events=1,
            min_validation_truth_events=1,
            min_truth_rate_lower_bound=0.0,
            min_survival_rate_lower_bound=0.0,
            confidence_z=0.0,
        ),
        min_calibration_execute_causal_changes=0,
        min_calibration_volatility_causal_changes=1,
        min_validation_execute_causal_changes=0,
        min_validation_volatility_causal_changes=0,
    )
    evaluation = evaluate_joint_policy_candidate(
        bundle,
        JointPolicyCandidate(execute_net_edge_bps=35.0, volatile_return_bps=20.0),
        policy,
        context,
        min_truth_events=0,
        min_execute_causal_changes=0,
        min_volatility_causal_changes=1,
    )

    assert evaluation.causal_support.execute_final_verdict_changes == 0
    assert evaluation.causal_support.volatility_regime_label_changes == 1
    assert evaluation.causal_support.volatility_final_verdict_changes == 0
    assert "INSUFFICIENT_VOLATILITY_CAUSAL_SUPPORT" in evaluation.reasons
    assert evaluation.eligible is False


def test_baseline_volatility_threshold_is_not_claimed_as_new_causal_support():
    bundle = _support_bundle()
    context = validate_joint_policy_context(bundle)
    policy = JointHoldoutPolicy(
        holdout=HoldoutPolicy(
            validation_fraction=0.5,
            min_calibration_operations=1,
            min_validation_operations=1,
            min_calibration_truth_events=1,
            min_validation_truth_events=1,
            min_truth_rate_lower_bound=0.0,
            min_survival_rate_lower_bound=0.0,
            confidence_z=0.0,
        ),
        min_calibration_execute_causal_changes=1,
        min_calibration_volatility_causal_changes=1,
        min_validation_execute_causal_changes=0,
        min_validation_volatility_causal_changes=0,
    )
    evaluation = evaluate_joint_policy_candidate(
        bundle,
        JointPolicyCandidate(execute_net_edge_bps=35.0, volatile_return_bps=75.0),
        policy,
        context,
        min_truth_events=1,
        min_execute_causal_changes=1,
        min_volatility_causal_changes=1,
    )

    assert evaluation.causal_support.volatility_regime_label_changes == 0
    assert evaluation.causal_support.volatility_final_verdict_changes == 0
    assert "INSUFFICIENT_VOLATILITY_CAUSAL_SUPPORT" in evaluation.reasons


def test_joint_holdout_selection_is_calibration_only_when_validation_outcomes_change():
    grid = JointCandidateGrid(
        execute_net_edge_bps=(35.0,),
        volatile_return_bps=(20.0, 50.0),
    )
    policy = _joint_policy()

    first = run_joint_holdout_calibration(_holdout_bundle(validation_flip=False), grid, policy)
    second = run_joint_holdout_calibration(_holdout_bundle(validation_flip=True), grid, policy)

    assert first.selected_candidate is not None
    assert first.selected_candidate == second.selected_candidate
    assert first.selected_candidate.volatile_return_bps == 20.0
    assert first.canonical_payload()["validation_not_used_for_selection"] is True
    assert first.canonical_payload()["causal_support_is_eligibility_not_objective"] is True


def test_validation_requires_out_of_sample_causal_support_when_requested():
    bundle = _holdout_bundle()
    grid = JointCandidateGrid(
        execute_net_edge_bps=(35.0,),
        volatile_return_bps=(20.0,),
    )
    policy = _joint_policy(validation_execute=2, validation_volatility=2)

    report = run_joint_holdout_calibration(bundle, grid, policy)

    assert report.status is JointHoldoutStatus.INSUFFICIENT_VALIDATION_CAUSAL_SUPPORT
    assert report.validation_evaluation is not None


def test_joint_report_digest_detects_causal_support_tampering():
    report = run_joint_holdout_calibration(
        _holdout_bundle(),
        JointCandidateGrid(execute_net_edge_bps=(35.0,), volatile_return_bps=(20.0,)),
        _joint_policy(),
    )
    envelope = deepcopy(report.to_envelope())
    envelope["payload"]["calibration_evaluations"][0]["causal_support"][
        "volatility_final_verdict_changes"
    ] += 1

    with pytest.raises(ValueError, match="SHA-256"):
        verify_joint_holdout_report_envelope(envelope)


def test_joint_context_requires_suppressive_volatile_gate():
    case = _case("bad-gate", 1, volatility="medium", edge_bps=39.0, realized_edge_bps=39.0)
    case = replace(
        case,
        regime_execution_policy=RegimeExecutionPolicy(
            normal=RegimeAction.ALLOW,
            volatile=RegimeAction.ALLOW,
        ),
    )

    with pytest.raises(ValueError, match="VOLATILE to be suppressive"):
        validate_joint_policy_context(ReplayBundle(cases=(case,)))
