from copy import deepcopy
from dataclasses import replace
import hashlib
import json

import pytest

from resonance_arbitrage_graph.engine import PaperExecution, Policy, evaluate_route
from resonance_arbitrage_graph.metrics import calculate_metrics
from resonance_arbitrage_graph.model import Verdict
from resonance_arbitrage_graph.observation import OutcomeClass, observation_from_evidence
from resonance_arbitrage_graph.quotes import CostAssumption, QuoteSnapshot, quote_to_trade_edges
from resonance_arbitrage_graph.regime import MarketRegime, RegimePolicy
from resonance_arbitrage_graph.regime_gate import (
    RegimeAction,
    RegimeExecutionPolicy,
    apply_regime_gate,
)
from resonance_arbitrage_graph.replay import (
    ReplayBundle,
    ReplayCase,
    ReplayLeg,
    ReplayOutcome,
    ReplaySide,
    replay_case,
)
from resonance_arbitrage_graph.rolling_state import RollingMarketWindow, RollingWindowPolicy
from resonance_arbitrage_graph.window_evidence import make_window_regime_evidence_receipt
from resonance_arbitrage_graph.window_regime import market_key
from resonance_arbitrage_graph.evidence import EvidenceReceipt


ZERO = CostAssumption(fee_bps=0.0, slippage_bps=0.0)
WINDOW_POLICY = RollingWindowPolicy(horizon_ms=60_000, min_samples=5, min_coverage_ratio=1.0)
_LEVEL = {Verdict.REJECT: 0, Verdict.OBSERVE: 1, Verdict.EXECUTE_SIM: 2}


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


def _series(symbol: str, base: str, quote: str, mids: list[float], spread: float):
    times = (0, 15_000, 30_000, 45_000, 60_000)
    quotes = tuple(_quote(symbol, base, quote, ts, mid, spread) for ts, mid in zip(times, mids))
    window = RollingMarketWindow.from_quotes(quotes, policy=WINDOW_POLICY, end_ms=60_000)
    return quotes, window


def _decision_state():
    btc, btc_window = _series("BTCUSDT", "BTC", "USDT", [99.99, 100.00, 99.98, 100.01, 99.995], 0.01)
    ethbtc, ethbtc_window = _series("ETHBTC", "ETH", "BTC", [0.49994, 0.49996, 0.49993, 0.49997, 0.49995], 0.0001)
    ethusdt, ethusdt_window = _series("ETHUSDT", "ETH", "USDT", [50.17, 50.18, 50.16, 50.19, 50.185], 0.01)
    snapshots = (btc[-1], ethbtc[-1], ethusdt[-1])
    windows = {
        market_key("fixture", "BTCUSDT"): btc_window,
        market_key("fixture", "ETHBTC"): ethbtc_window,
        market_key("fixture", "ETHUSDT"): ethusdt_window,
    }
    btc_buy, _ = quote_to_trade_edges(snapshots[0], ZERO, now_ms=60_000)
    eth_buy, _ = quote_to_trade_edges(snapshots[1], ZERO, now_ms=60_000)
    _, eth_sell = quote_to_trade_edges(snapshots[2], ZERO, now_ms=60_000)
    route = (btc_buy, eth_buy, eth_sell)
    result = evaluate_route(route, 1_000.0, policy=Policy())
    legs = (
        ReplayLeg(0, ReplaySide.BUY, ZERO),
        ReplayLeg(1, ReplaySide.BUY, ZERO),
        ReplayLeg(2, ReplaySide.SELL, ZERO),
    )
    return snapshots, windows, route, result, legs


def _replay_case(
    operation: str,
    *,
    attempt: int = 1,
    realized_edge_bps: float | None = 40.0,
    gate_policy: RegimeExecutionPolicy | None = None,
) -> ReplayCase:
    snapshots, windows, _route, _result, legs = _decision_state()
    return ReplayCase(
        case_id=f"{operation}-a{attempt}",
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
        regime_execution_policy=gate_policy or RegimeExecutionPolicy(),
        outcome=ReplayOutcome(
            observed_at_ms=61_000 + attempt,
            realized_net_edge_bps=realized_edge_bps,
        ),
    )


def test_default_regime_actions_are_monotonic_for_every_base_verdict():
    policy = RegimeExecutionPolicy()
    for base in Verdict:
        for regime in MarketRegime:
            result = apply_regime_gate(base, regime, policy=policy)
            assert _LEVEL[result.final_verdict] <= _LEVEL[base]


def test_each_configurable_action_is_monotonic():
    for base in Verdict:
        for action in RegimeAction:
            policy = RegimeExecutionPolicy(normal=action)
            result = apply_regime_gate(base, MarketRegime.NORMAL, policy=policy)
            assert _LEVEL[result.final_verdict] <= _LEVEL[base]
            if base is Verdict.REJECT:
                assert result.final_verdict is Verdict.REJECT
            if base is Verdict.OBSERVE:
                assert result.final_verdict is not Verdict.EXECUTE_SIM


def test_default_execute_gate_behavior():
    policy = RegimeExecutionPolicy()
    assert apply_regime_gate(Verdict.EXECUTE_SIM, MarketRegime.NORMAL, policy=policy).final_verdict is Verdict.EXECUTE_SIM
    assert apply_regime_gate(Verdict.EXECUTE_SIM, MarketRegime.VOLATILE, policy=policy).final_verdict is Verdict.OBSERVE
    assert apply_regime_gate(Verdict.EXECUTE_SIM, MarketRegime.THIN_LIQUIDITY, policy=policy).final_verdict is Verdict.OBSERVE
    assert apply_regime_gate(Verdict.EXECUTE_SIM, MarketRegime.DISLOCATED, policy=policy).final_verdict is Verdict.OBSERVE
    assert apply_regime_gate(Verdict.EXECUTE_SIM, MarketRegime.UNKNOWN, policy=policy).final_verdict is Verdict.REJECT


def test_unknown_cannot_be_configured_to_allow():
    with pytest.raises(ValueError, match="UNKNOWN"):
        RegimeExecutionPolicy(unknown=RegimeAction.ALLOW)


def test_gate_policy_changes_evidence_digest_and_final_verdict():
    snapshots, windows, route, result, _legs = _decision_state()
    allow = make_window_regime_evidence_receipt(
        "allow",
        route,
        result,
        snapshots=snapshots,
        windows_by_market=windows,
        evaluation_time_ms=60_000,
        regime_execution_policy=RegimeExecutionPolicy(),
    )
    observe = make_window_regime_evidence_receipt(
        "observe",
        route,
        result,
        snapshots=snapshots,
        windows_by_market=windows,
        evaluation_time_ms=60_000,
        regime_execution_policy=RegimeExecutionPolicy(normal=RegimeAction.OBSERVE_ONLY),
    )

    assert allow.payload["expected"]["base_verdict"] == "EXECUTE_SIM"
    assert allow.payload["expected"]["verdict"] == "EXECUTE_SIM"
    assert observe.payload["expected"]["base_verdict"] == "EXECUTE_SIM"
    assert observe.payload["expected"]["verdict"] == "OBSERVE"
    assert allow.sha256 != observe.sha256
    assert allow.payload["regime_execution_gate"]["policy_sha256"] != observe.payload["regime_execution_gate"]["policy_sha256"]


def test_observation_memory_uses_final_post_gate_verdict_for_truth_denominator():
    snapshots, windows, route, result, _legs = _decision_state()
    execution = PaperExecution(
        operation_id="memory",
        expected=result,
        realized_final_amount=1_004.0,
        realized_net_edge=0.004,
        prediction_error=0.004 - result.net_edge,
    )
    allowed_receipt = make_window_regime_evidence_receipt(
        "memory",
        route,
        result,
        snapshots=snapshots,
        windows_by_market=windows,
        evaluation_time_ms=60_000,
        execution=execution,
    )
    downgraded_execution = replace(execution, operation_id="memory-observe")
    downgraded_receipt = make_window_regime_evidence_receipt(
        "memory-observe",
        route,
        result,
        snapshots=snapshots,
        windows_by_market=windows,
        evaluation_time_ms=60_000,
        regime_execution_policy=RegimeExecutionPolicy(normal=RegimeAction.OBSERVE_ONLY),
        execution=downgraded_execution,
    )

    allowed = observation_from_evidence(
        allowed_receipt,
        execution_id="exec-allow",
        attempt=1,
        opportunity_id="opp-allow",
        route_id="route",
        detected_at_ms=60_000,
        observed_at_ms=61_000,
        required_edge_bps=30.0,
    )
    downgraded = observation_from_evidence(
        downgraded_receipt,
        execution_id="exec-observe",
        attempt=1,
        opportunity_id="opp-observe",
        route_id="route",
        detected_at_ms=60_000,
        observed_at_ms=61_000,
        required_edge_bps=30.0,
    )

    assert allowed.outcome_class is OutcomeClass.TRUE_POSITIVE
    assert downgraded.expected_verdict == "OBSERVE"
    assert downgraded.outcome_class is OutcomeClass.INDETERMINATE
    assert downgraded.market_context["base_verdict"] == "EXECUTE_SIM"
    assert downgraded.market_context["final_verdict"] == "OBSERVE"
    metrics = calculate_metrics((allowed, downgraded))
    assert metrics.true_positive == 1
    assert metrics.indeterminate == 1
    assert metrics.opportunity_truth_rate == pytest.approx(1.0)


def test_observation_rejects_self_consistent_hash_with_forged_gate_decision():
    snapshots, windows, route, result, _legs = _decision_state()
    receipt = make_window_regime_evidence_receipt(
        "forged",
        route,
        result,
        snapshots=snapshots,
        windows_by_market=windows,
        evaluation_time_ms=60_000,
    )
    payload = deepcopy(receipt.payload)
    payload["regime_execution_gate"]["action"] = "REJECT"
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
    forged = EvidenceReceipt(payload=payload, sha256=hashlib.sha256(canonical.encode("utf-8")).hexdigest())

    with pytest.raises(ValueError, match="inconsistent with policy"):
        observation_from_evidence(
            forged,
            execution_id="exec-forged",
            attempt=1,
            opportunity_id="opp-forged",
            route_id="route",
            detected_at_ms=60_000,
            observed_at_ms=61_000,
            required_edge_bps=30.0,
        )


def test_replay_recomputes_gate_and_uses_final_verdict():
    case = _replay_case(
        "replay-gate",
        gate_policy=RegimeExecutionPolicy(normal=RegimeAction.OBSERVE_ONLY),
    )
    result = replay_case(case)

    assert result.regime is MarketRegime.NORMAL
    assert result.base_verdict is Verdict.EXECUTE_SIM
    assert result.regime_action is RegimeAction.OBSERVE_ONLY
    assert result.expected_verdict is Verdict.OBSERVE
    assert result.outcome_class is OutcomeClass.INDETERMINATE


def test_retry_cannot_drift_regime_execution_policy():
    first = _replay_case("gate-drift", attempt=1, realized_edge_bps=None)
    second = _replay_case(
        "gate-drift",
        attempt=2,
        realized_edge_bps=40.0,
        gate_policy=RegimeExecutionPolicy(normal=RegimeAction.OBSERVE_ONLY),
    )

    with pytest.raises(ValueError, match="drifted"):
        ReplayBundle(cases=(first, second))


def test_incomplete_window_becomes_unknown_reject_in_replay():
    case = _replay_case("unknown")
    key = market_key("fixture", "BTCUSDT")
    original = case.windows_by_market[key]
    windows = dict(case.windows_by_market)
    windows[key] = RollingMarketWindow(
        policy=replace(original.policy, min_samples=5, min_coverage_ratio=0.8),
        samples=original.samples[-2:],
    )
    result = replay_case(replace(case, windows_by_market=windows))

    assert result.regime is MarketRegime.UNKNOWN
    assert result.regime_action is RegimeAction.REJECT
    assert result.base_verdict is Verdict.EXECUTE_SIM
    assert result.expected_verdict is Verdict.REJECT
    assert result.outcome_class is OutcomeClass.REJECTED
