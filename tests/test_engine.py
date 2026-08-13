from dataclasses import replace
import math

import pytest

from resonance_arbitrage_graph import (
    Edge,
    MarketGraph,
    Node,
    PaperExecutor,
    Policy,
    ReplayError,
    Verdict,
    evaluate_route,
    make_evidence_receipt,
)


def profitable_triangle():
    usdt = Node("CEX", "USDT")
    btc = Node("CEX", "BTC")
    eth = Node("CEX", "ETH")
    return [
        Edge(usdt, btc, rate=1 / 80_000, fee_bps=5, slippage_bps=5),
        Edge(btc, eth, rate=20.0, fee_bps=5, slippage_bps=5),
        Edge(eth, usdt, rate=4_050, fee_bps=5, slippage_bps=5),
    ]


def test_graph_finds_profitable_triangle():
    route = profitable_triangle()
    graph = MarketGraph(route)

    cycles = graph.find_cycles(route[0].src, max_hops=3)

    assert len(cycles) == 1
    result = evaluate_route(cycles[0], 10_000)
    assert result.verdict is Verdict.EXECUTE_SIM
    assert result.net_edge > 0


def test_visible_spread_can_be_false_after_costs():
    usdt = Node("CEX", "USDT")
    eth = Node("CEX", "ETH")
    route = [
        Edge(usdt, eth, rate=1 / 4_000, fee_bps=20, slippage_bps=25),
        Edge(eth, usdt, rate=4_030, fee_bps=20, slippage_bps=25),
    ]

    result = evaluate_route(route, 10_000)

    assert result.gross_edge > 0
    assert result.net_edge < 0
    assert result.verdict is Verdict.REJECT
    assert "NON_POSITIVE_NET_EDGE" in result.reasons


def test_stale_quote_is_rejected_even_when_route_is_profitable():
    route = profitable_triangle()
    route[1] = replace(route[1], quote_age_ms=3_001)

    result = evaluate_route(route, 10_000)

    assert result.verdict is Verdict.REJECT
    assert "STALE_QUOTE:1" in result.reasons


def test_capacity_limit_is_causal_constraint():
    route = profitable_triangle()
    route[0] = replace(route[0], capacity=5_000)

    result = evaluate_route(route, 10_000)

    assert result.verdict is Verdict.REJECT
    assert "CAPACITY_EXCEEDED:0" in result.reasons


def test_route_latency_can_invalidate_positive_edge():
    route = [replace(edge, latency_ms=2_000) for edge in profitable_triangle()]

    result = evaluate_route(route, 10_000)

    assert result.net_edge > 0
    assert result.verdict is Verdict.REJECT
    assert "ROUTE_LATENCY_EXCEEDED" in result.reasons


def test_paper_executor_blocks_replay_and_models_extra_slippage():
    route = profitable_triangle()
    executor = PaperExecutor()

    execution = executor.execute(
        "arb-001",
        route,
        10_000,
        extra_slippage_bps=3,
    )

    assert execution.realized_net_edge < execution.expected.net_edge
    assert execution.prediction_error < 0

    with pytest.raises(ReplayError):
        executor.execute("arb-001", route, 10_000)


def test_evidence_receipt_is_deterministic():
    route = profitable_triangle()
    result = evaluate_route(route, 10_000)

    first = make_evidence_receipt("arb-001", route, result)
    second = make_evidence_receipt("arb-001", route, result)

    assert first.sha256 == second.sha256
    assert first.canonical_json() == second.canonical_json()
    assert first.payload["paper_only"] is True
    assert first.payload["invariants"]["returns_to_start"] is True


@pytest.mark.parametrize("amount", [math.inf, -math.inf, math.nan])
def test_non_finite_capital_is_rejected(amount):
    with pytest.raises(ValueError, match="finite and positive"):
        evaluate_route(profitable_triangle(), amount)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"execute_net_edge": 0.0},
        {"execute_net_edge": -0.01},
        {"execute_net_edge": math.nan},
        {"observe_net_edge": -0.01},
        {"execute_net_edge": 0.001, "observe_net_edge": 0.001},
        {"max_quote_age_ms": -1},
        {"max_route_latency_ms": -1},
        {"min_success_probability": 1.01},
    ],
)
def test_invalid_policy_cannot_weaken_profitability_invariants(kwargs):
    with pytest.raises(ValueError):
        Policy(**kwargs)
