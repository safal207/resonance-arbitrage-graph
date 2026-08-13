from __future__ import annotations

from collections.abc import Sequence
import math

from .quotes import QuoteSnapshot
from .regime import RegimeFeatures


def _spread_bps(quote: QuoteSnapshot) -> float:
    mid = (quote.bid + quote.ask) / 2.0
    if mid <= 0 or not math.isfinite(mid):
        raise ValueError("quote midpoint must be finite and positive")
    return (quote.ask - quote.bid) / mid * 10_000.0


def derive_regime_features(
    quotes: Sequence[QuoteSnapshot],
    *,
    evaluation_time_ms: int,
    reference_amount: float,
    cross_rate_dislocation_bps: float | None = None,
    short_window_return_volatility_bps: float | None = None,
) -> RegimeFeatures:
    if not quotes:
        raise ValueError("at least one quote is required")
    if evaluation_time_ms < 0:
        raise ValueError("evaluation_time_ms must be non-negative")
    if not math.isfinite(reference_amount) or reference_amount <= 0:
        raise ValueError("reference_amount must be finite and positive")

    spreads: list[float] = []
    capacities: list[float] = []
    ages: list[int] = []

    for quote in quotes:
        spreads.append(_spread_bps(quote))

        # Conservatively use the smaller top-of-book side. This is a screening
        # capacity indicator only; route execution still uses direction-specific
        # edge capacity in the verifier.
        top_capacity = min(quote.bid_qty, quote.ask_qty)
        if not math.isfinite(top_capacity) or top_capacity <= 0:
            raise ValueError("quote top-of-book quantity must be finite and positive")
        capacities.append(top_capacity / reference_amount)

        observed_at_ms = quote.observed_at_ms
        if observed_at_ms > evaluation_time_ms:
            raise ValueError("quote observation time cannot be in the future")
        ages.append(evaluation_time_ms - observed_at_ms)

    return RegimeFeatures(
        normalized_spread_bps=max(spreads),
        top_of_book_capacity_ratio=min(capacities),
        quote_age_ms=max(ages),
        quote_age_dispersion_ms=max(ages) - min(ages),
        cross_rate_dislocation_bps=cross_rate_dislocation_bps,
        short_window_return_volatility_bps=short_window_return_volatility_bps,
    )
