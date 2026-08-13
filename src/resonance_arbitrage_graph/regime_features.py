from __future__ import annotations

from collections.abc import Sequence
import math

from .market_evidence import bind_route_to_snapshots
from .model import Edge
from .quotes import QuoteSnapshot
from .regime import RegimeFeatures


def _spread_bps(quote: QuoteSnapshot) -> float:
    mid = (quote.bid_price + quote.ask_price) / 2.0
    if mid <= 0 or not math.isfinite(mid):
        raise ValueError("quote midpoint must be finite and positive")
    return (quote.ask_price - quote.bid_price) / mid * 10_000.0


def derive_route_regime_features(
    edges: Sequence[Edge],
    snapshots: Sequence[QuoteSnapshot],
    *,
    evaluation_time_ms: int,
    start_amount: float,
    cross_rate_dislocation_bps: float | None = None,
    short_window_return_volatility_bps: float | None = None,
) -> RegimeFeatures:
    """Derive candidate-specific regime features from exact route provenance.

    Capacity is normalized leg-by-leg in each edge's source-asset units. This avoids
    comparing raw quantities from different assets as if they shared one unit.
    """

    if not edges:
        raise ValueError("route must contain at least one edge")
    if not snapshots:
        raise ValueError("at least one quote snapshot is required")
    if evaluation_time_ms < 0:
        raise ValueError("evaluation_time_ms must be non-negative")
    if not math.isfinite(start_amount) or start_amount <= 0:
        raise ValueError("start_amount must be finite and positive")

    bindings = bind_route_to_snapshots(
        edges,
        snapshots,
        evaluation_time_ms=evaluation_time_ms,
    )

    route_snapshots = [snapshots[item["snapshot_index"]] for item in bindings]
    for snapshot in route_snapshots:
        if snapshot.freshness_reference_ms > evaluation_time_ms:
            raise ValueError("quote freshness reference cannot be in the future")

    spreads = [_spread_bps(snapshot) for snapshot in route_snapshots]
    ages = [snapshot.age_ms(evaluation_time_ms) for snapshot in route_snapshots]

    current_amount = start_amount
    capacity_ratios: list[float] = []
    for edge in edges:
        ratio = edge.capacity / current_amount
        if not math.isfinite(ratio) or ratio <= 0:
            raise ValueError("route capacity ratio must be finite and positive")
        capacity_ratios.append(ratio)

        current_amount = (
            current_amount
            * edge.rate
            * (1.0 - edge.total_cost_bps / 10_000.0)
        )
        if not math.isfinite(current_amount) or current_amount <= 0:
            raise ValueError("route amount became non-finite or non-positive")

    return RegimeFeatures(
        normalized_spread_bps=max(spreads),
        top_of_book_capacity_ratio=min(capacity_ratios),
        quote_age_ms=max(ages),
        quote_age_dispersion_ms=max(ages) - min(ages),
        cross_rate_dislocation_bps=cross_rate_dislocation_bps,
        short_window_return_volatility_bps=short_window_return_volatility_bps,
    )
