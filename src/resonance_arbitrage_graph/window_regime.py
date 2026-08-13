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
from .rolling_state import RollingMarketSample, RollingMarketWindow, RollingWindowSummary


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
    indices_by_market: dict[str, list[int]] = {}
    for index in bound_indices:
        snapshot = snapshots[index]
        indices_by_market.setdefault(market_key(snapshot.venue, snapshot.symbol), []).append(index)

    summaries: dict[str, RollingWindowSummary] = {}
    digests: dict[str, str] = {}
    volatilities: list[float] = []
    incomplete_reasons: list[str] = []

    for key in sorted(indices_by_market):
        try:
            window = windows_by_market[key]
        except KeyError as exc:
            raise ValueError(f"missing rolling window for route market: {key}") from exc

        expected_samples = {
            RollingMarketSample.from_quote(snapshots[index])
            for index in indices_by_market[key]
        }
        if len(expected_samples) != 1:
            raise ValueError(f"ambiguous current route snapshot for market: {key}")
        expected_tail = next(iter(expected_samples))
        if window.samples[-1] != expected_tail:
            raise ValueError(f"rolling window tail does not match current route snapshot: {key}")

        summary = window.summary(evaluation_time_ms=evaluation_time_ms)
        summaries[key] = summary
        digests[key] = window.sha256
        if not summary.complete or summary.short_window_return_volatility_bps is None:
            incomplete_reasons.extend(f"{key}:{reason}" for reason in summary.reasons)
        else:
            volatilities.append(summary.short_window_return_volatility_bps)

    if incomplete_reasons:
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
                reasons=("rolling_window_incomplete", *incomplete_reasons),
            ),
            window_sha256_by_market=digests,
            window_summary_by_market=summaries,
        )

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
