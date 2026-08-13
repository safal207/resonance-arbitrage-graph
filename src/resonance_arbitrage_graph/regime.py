from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
import json
import math
from typing import Any


class MarketRegime(str, Enum):
    NORMAL = "NORMAL"
    VOLATILE = "VOLATILE"
    THIN_LIQUIDITY = "THIN_LIQUIDITY"
    DISLOCATED = "DISLOCATED"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True, slots=True)
class RegimePolicy:
    volatile_return_bps: float = 75.0
    thin_capacity_ratio: float = 1.25
    dislocated_cross_rate_bps: float = 40.0
    wide_spread_bps: float = 25.0
    max_quote_age_ms: int = 3_000
    max_quote_age_dispersion_ms: int = 1_500

    def __post_init__(self) -> None:
        for name in (
            "volatile_return_bps",
            "thin_capacity_ratio",
            "dislocated_cross_rate_bps",
            "wide_spread_bps",
        ):
            value = getattr(self, name)
            if not math.isfinite(value) or value < 0:
                raise ValueError(f"{name} must be finite and non-negative")
        if self.max_quote_age_ms < 0:
            raise ValueError("max_quote_age_ms must be non-negative")
        if self.max_quote_age_dispersion_ms < 0:
            raise ValueError("max_quote_age_dispersion_ms must be non-negative")


@dataclass(frozen=True, slots=True)
class RegimeFeatures:
    normalized_spread_bps: float
    top_of_book_capacity_ratio: float
    quote_age_ms: int
    quote_age_dispersion_ms: int
    cross_rate_dislocation_bps: float | None = None
    short_window_return_volatility_bps: float | None = None

    def __post_init__(self) -> None:
        for name in ("normalized_spread_bps", "top_of_book_capacity_ratio"):
            value = getattr(self, name)
            if not math.isfinite(value) or value < 0:
                raise ValueError(f"{name} must be finite and non-negative")
        if self.top_of_book_capacity_ratio == 0:
            raise ValueError("top_of_book_capacity_ratio must be positive")
        if self.quote_age_ms < 0 or self.quote_age_dispersion_ms < 0:
            raise ValueError("quote ages cannot be negative")
        for name in (
            "cross_rate_dislocation_bps",
            "short_window_return_volatility_bps",
        ):
            value = getattr(self, name)
            if value is not None and (not math.isfinite(value) or value < 0):
                raise ValueError(f"{name} must be finite and non-negative when supplied")

    def to_context(self) -> dict[str, Any]:
        payload = asdict(self)
        json.dumps(payload, sort_keys=True, allow_nan=False)
        return payload


@dataclass(frozen=True, slots=True)
class RegimeClassification:
    regime: MarketRegime
    features: RegimeFeatures
    reasons: tuple[str, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.regime, MarketRegime):
            raise ValueError("regime must be a MarketRegime")
        if not isinstance(self.features, RegimeFeatures):
            raise ValueError("features must be RegimeFeatures")
        if not self.reasons or any(
            not isinstance(reason, str) or not reason
            for reason in self.reasons
        ):
            raise ValueError("reasons must contain non-empty strings")

    def to_market_context(self) -> dict[str, Any]:
        return {
            "regime": self.regime.value,
            "regime_features": self.features.to_context(),
            "regime_reasons": list(self.reasons),
        }


def merge_regime_context(
    base_context: dict[str, Any],
    classification: RegimeClassification,
) -> dict[str, Any]:
    """Attach derived regime context without allowing caller override/drift."""

    context = dict(base_context)
    derived = classification.to_market_context()
    for key, value in derived.items():
        if key in context and context[key] != value:
            raise ValueError(f"market_context conflicts with derived regime field: {key}")
        context[key] = value
    try:
        json.dumps(context, sort_keys=True, ensure_ascii=False, allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise ValueError("merged market_context must be strict JSON") from exc
    return context


def classify_market_regime(
    features: RegimeFeatures,
    *,
    policy: RegimePolicy | None = None,
) -> RegimeClassification:
    policy = policy or RegimePolicy()
    reasons: list[str] = []

    if features.quote_age_ms > policy.max_quote_age_ms:
        reasons.append("stale_quote")
    if features.quote_age_dispersion_ms > policy.max_quote_age_dispersion_ms:
        reasons.append("quote_age_dispersion")

    # Classification is fail-closed when freshness evidence is not good enough.
    if reasons:
        return RegimeClassification(
            regime=MarketRegime.UNKNOWN,
            features=features,
            reasons=tuple(reasons),
        )

    # Precedence is deliberate: severe state divergence outranks ordinary
    # volatility, and thin executable depth outranks a merely volatile tape.
    if (
        features.cross_rate_dislocation_bps is not None
        and features.cross_rate_dislocation_bps >= policy.dislocated_cross_rate_bps
    ):
        return RegimeClassification(
            regime=MarketRegime.DISLOCATED,
            features=features,
            reasons=("cross_rate_dislocation",),
        )

    if (
        features.top_of_book_capacity_ratio <= policy.thin_capacity_ratio
        or features.normalized_spread_bps >= policy.wide_spread_bps
    ):
        thin_reasons: list[str] = []
        if features.top_of_book_capacity_ratio <= policy.thin_capacity_ratio:
            thin_reasons.append("low_capacity_ratio")
        if features.normalized_spread_bps >= policy.wide_spread_bps:
            thin_reasons.append("wide_spread")
        return RegimeClassification(
            regime=MarketRegime.THIN_LIQUIDITY,
            features=features,
            reasons=tuple(thin_reasons),
        )

    if features.short_window_return_volatility_bps is None:
        return RegimeClassification(
            regime=MarketRegime.UNKNOWN,
            features=features,
            reasons=("volatility_feature_missing",),
        )

    if features.short_window_return_volatility_bps >= policy.volatile_return_bps:
        return RegimeClassification(
            regime=MarketRegime.VOLATILE,
            features=features,
            reasons=("return_volatility",),
        )

    return RegimeClassification(
        regime=MarketRegime.NORMAL,
        features=features,
        reasons=("within_normal_thresholds",),
    )
