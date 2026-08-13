from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Sequence
import math

from .model import Edge, RouteResult, Verdict


@dataclass(frozen=True, slots=True)
class Policy:
    execute_net_edge: float = 0.003
    observe_net_edge: float = 0.0
    max_quote_age_ms: int = 3_000
    max_route_latency_ms: int = 5_000
    min_success_probability: float = 0.75

    def __post_init__(self) -> None:
        if not math.isfinite(self.execute_net_edge) or self.execute_net_edge <= 0:
            raise ValueError("execute_net_edge must be finite and positive")
        if not math.isfinite(self.observe_net_edge) or self.observe_net_edge < 0:
            raise ValueError("observe_net_edge must be finite and non-negative")
        if self.execute_net_edge <= self.observe_net_edge:
            raise ValueError("execute_net_edge must be greater than observe_net_edge")
        if self.max_quote_age_ms < 0:
            raise ValueError("max_quote_age_ms cannot be negative")
        if self.max_route_latency_ms < 0:
            raise ValueError("max_route_latency_ms cannot be negative")
        if not math.isfinite(self.min_success_probability) or not 0.0 <= self.min_success_probability <= 1.0:
            raise ValueError("min_success_probability must be between 0 and 1")


@dataclass(frozen=True, slots=True)
class PaperExecution:
    operation_id: str
    expected: RouteResult
    realized_final_amount: float
    realized_net_edge: float
    prediction_error: float


class ReplayError(RuntimeError):
    pass


def evaluate_route(
    edges: Sequence[Edge],
    amount: float,
    *,
    policy: Policy | None = None,
) -> RouteResult:
    if not math.isfinite(amount) or amount <= 0:
        raise ValueError("amount must be finite and positive")
    if not edges:
        raise ValueError("route must contain at least one edge")

    for previous, current in zip(edges, edges[1:]):
        if previous.dst != current.src:
            raise ValueError("route edges are not causally continuous")

    active_policy = policy or Policy()
    reasons: list[str] = []

    if edges[-1].dst != edges[0].src:
        reasons.append("NOT_A_CYCLE")

    gross_final = amount
    final = amount
    success_probability = 1.0
    total_latency_ms = 0

    for index, edge in enumerate(edges):
        gross_final *= edge.rate

        if edge.quote_age_ms > active_policy.max_quote_age_ms:
            reasons.append(f"STALE_QUOTE:{index}")
        if final > edge.capacity:
            reasons.append(f"CAPACITY_EXCEEDED:{index}")

        final *= edge.rate * (1.0 - edge.total_cost_bps / 10_000.0)
        success_probability *= edge.success_probability
        total_latency_ms += edge.latency_ms

    if total_latency_ms > active_policy.max_route_latency_ms:
        reasons.append("ROUTE_LATENCY_EXCEEDED")
    if success_probability < active_policy.min_success_probability:
        reasons.append("SUCCESS_PROBABILITY_TOO_LOW")

    gross_edge = gross_final / amount - 1.0
    net_edge = final / amount - 1.0
    risk_adjusted_edge = net_edge * success_probability

    if reasons:
        verdict = Verdict.REJECT
    elif net_edge >= active_policy.execute_net_edge:
        verdict = Verdict.EXECUTE_SIM
    elif net_edge > active_policy.observe_net_edge:
        verdict = Verdict.OBSERVE
    else:
        reasons.append("NON_POSITIVE_NET_EDGE")
        verdict = Verdict.REJECT

    return RouteResult(
        start_amount=amount,
        gross_final_amount=gross_final,
        final_amount=final,
        gross_edge=gross_edge,
        net_edge=net_edge,
        risk_adjusted_edge=risk_adjusted_edge,
        success_probability=success_probability,
        total_latency_ms=total_latency_ms,
        verdict=verdict,
        reasons=tuple(reasons),
    )


class PaperExecutor:
    """Deterministic executor with no live trading code path."""

    def __init__(self) -> None:
        self._seen_operation_ids: set[str] = set()

    def execute(
        self,
        operation_id: str,
        edges: Sequence[Edge],
        amount: float,
        *,
        policy: Policy | None = None,
        extra_slippage_bps: float = 0.0,
    ) -> PaperExecution:
        if not operation_id:
            raise ValueError("operation_id must be non-empty")
        if operation_id in self._seen_operation_ids:
            raise ReplayError(f"operation already executed: {operation_id}")

        expected = evaluate_route(edges, amount, policy=policy)
        if expected.verdict is not Verdict.EXECUTE_SIM:
            raise ValueError(f"route is not executable in simulation: {expected.verdict.value}")

        realized = amount
        for edge in edges:
            realized = edge.apply(realized, extra_slippage_bps=extra_slippage_bps)

        self._seen_operation_ids.add(operation_id)
        realized_net_edge = realized / amount - 1.0

        return PaperExecution(
            operation_id=operation_id,
            expected=expected,
            realized_final_amount=realized,
            realized_net_edge=realized_net_edge,
            prediction_error=realized_net_edge - expected.net_edge,
        )
