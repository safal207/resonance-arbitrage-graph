from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Mapping, Sequence
import math

from .market_evidence import bind_route_to_snapshots
from .model import Edge
from .quotes import QuoteSnapshot
from .regime import (
    MarketRegime,
    RegimeClassification,
    RegimePolicy,
    classify_market_regime,
)
from .regime_features import derive_route_regime_features
from .rolling_state import RollingMarketWindow, RollingWindowSummary


@dataclass(frozen=True, slots=True)
class WindowRegimeContext:
    classification: RegimeClassification
    window_sha256_by_market: dict[str, str]
    window_summary_by_market: dict[str, RollingWindowSummary]


def market_key(venue: str, symbol: str) -> str:
    return f"{venue}:{symbol}"


def derive_window_regime_context(
    edges: Sequence[Edge],
    snapshots: Sequence[QuoteSnapshot],
    *,
    windows_by_market: Mapping[str, RollingMarketWindow],
    evaluation_time_ms: int,
    start_amount: float,
    regime_policy: RegimePolicy | None = None,
) -> WindowRegimeContext:
    if not edges:
        raise ValueError("route must contain at least one edge")

    bindings = bind_route_to_snapshots(
        edges,
        snapshots,
        evaluation_time_ms=evaluation_time_ms,
    )
    bound_indices = sorted({binding["snapshot_index"] for binding in bindings})
    route_markets = {
        market_key(snapshots[index].venue, snapshots[index].symbol)
        for index in bound_indices
    }

    summaries: dict[str, RollingWindowSummary] = {}
    digests: dict[str, str] = {}
    volatilities: list[float] = []

    for key in sorted(route_markets):
        try:
            window = windows_by_market[key]
        except KeyError as exc:
            raise ValueError(f"missing rolling window for route market: {key}") from exc
        summary = window.summary(evaluation_time_ms=evaluation_time_ms)
        summaries[key] = summary
        digests[key] = window.sha256
        if not summary.complete or summary.short_window_return_volatility_bps is None:
            features = derive_route_regime_features(
                edges,
                snapshots,
                evaluation_time_ms=evaluation_time_ms,
                start_amount=start_amount,
                short_window_return_volatility_bps=None,
            )
            return WindowRegimeContext(
                classification=RegimeClassification(
                    regime=MarketRegime.UNKNOWN,
                    features=features,
                    reasons=("rolling_window_incomplete", *summary.reasons),
                ),
                window_sha256_by_market=digests,
                window_summary_by_market=summaries,
            )
        volatilities.append(summary.short_window_return_volatility_bps)

    if not volatilities or any(not math.isfinite(value) for value in volatilities):
        raise ValueError("rolling windows did not produce finite volatility")

    features = derive_route_regime_features(
        edges,
        snapshots,
        evaluation_time_ms=evaluation_time_ms,
        start_amount=start_amount,
        short_window_return_volatility_bps=max(volatilities),
    )
    classification = classify_market_regime(features, policy=regime_policy)
    return WindowRegimeContext(
        classification=classification,
        window_sha256_by_market=digests,
        window_summary_by_market=summaries,
    )
