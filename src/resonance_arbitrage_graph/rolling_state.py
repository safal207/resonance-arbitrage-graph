from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
import math
from statistics import pstdev
from typing import Any, Iterable

from .quotes import QuoteSnapshot


@dataclass(frozen=True, slots=True)
class RollingWindowPolicy:
    horizon_ms: int = 60_000
    min_samples: int = 5
    min_coverage_ratio: float = 0.8

    def __post_init__(self) -> None:
        if self.horizon_ms <= 0:
            raise ValueError("horizon_ms must be positive")
        if self.min_samples < 2:
            raise ValueError("min_samples must be >= 2")
        if not math.isfinite(self.min_coverage_ratio) or not 0.0 < self.min_coverage_ratio <= 1.0:
            raise ValueError("min_coverage_ratio must be finite and in (0, 1]")


@dataclass(frozen=True, slots=True)
class RollingMarketSample:
    venue: str
    symbol: str
    base_asset: str
    quote_asset: str
    observed_at_ms: int
    timestamp_class: str
    source_timestamp_ms: int | None
    freshness_reference_ms: int
    source_url: str
    metadata_url: str | None
    bid_price: float
    bid_qty: float
    ask_price: float
    ask_qty: float

    @classmethod
    def from_quote(cls, quote: QuoteSnapshot) -> "RollingMarketSample":
        return cls(
            venue=quote.venue,
            symbol=quote.symbol,
            base_asset=quote.base_asset,
            quote_asset=quote.quote_asset,
            observed_at_ms=quote.observed_at_ms,
            timestamp_class=quote.timestamp_class,
            source_timestamp_ms=quote.source_timestamp_ms,
            freshness_reference_ms=quote.freshness_reference_ms,
            source_url=quote.source_url,
            metadata_url=quote.metadata_url,
            bid_price=quote.bid_price,
            bid_qty=quote.bid_qty,
            ask_price=quote.ask_price,
            ask_qty=quote.ask_qty,
        )

    def __post_init__(self) -> None:
        for name in (
            "venue",
            "symbol",
            "base_asset",
            "quote_asset",
            "timestamp_class",
            "source_url",
        ):
            if not getattr(self, name):
                raise ValueError(f"{name} must be non-empty")
        if self.metadata_url is not None and not self.metadata_url:
            raise ValueError("metadata_url must be non-empty when provided")
        if self.observed_at_ms < 0 or self.freshness_reference_ms < 0:
            raise ValueError("sample timestamps cannot be negative")
        if self.source_timestamp_ms is not None and self.source_timestamp_ms < 0:
            raise ValueError("source_timestamp_ms cannot be negative")
        for name in ("bid_price", "bid_qty", "ask_price", "ask_qty"):
            value = getattr(self, name)
            if not math.isfinite(value) or value <= 0:
                raise ValueError(f"{name} must be finite and positive")
        if self.ask_price < self.bid_price:
            raise ValueError("ask_price cannot be below bid_price")

    @property
    def mid_price(self) -> float:
        return (self.bid_price + self.ask_price) / 2.0

    @property
    def spread_bps(self) -> float:
        return (self.ask_price - self.bid_price) / self.mid_price * 10_000.0

    @property
    def top_book_notional_quote(self) -> float:
        return min(self.bid_price * self.bid_qty, self.ask_price * self.ask_qty)

    def to_payload(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class RollingWindowSummary:
    venue: str
    symbol: str
    base_asset: str
    quote_asset: str
    start_ms: int
    end_ms: int
    horizon_ms: int
    sample_count: int
    coverage_ratio: float
    short_window_return_volatility_bps: float | None
    max_spread_bps: float
    mean_spread_bps: float
    min_top_book_notional_quote: float
    max_quote_age_ms: int
    quote_age_dispersion_ms: int
    complete: bool
    reasons: tuple[str, ...]

    def to_payload(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["reasons"] = list(self.reasons)
        return payload


@dataclass(frozen=True, slots=True)
class RollingMarketWindow:
    policy: RollingWindowPolicy
    samples: tuple[RollingMarketSample, ...]

    def __post_init__(self) -> None:
        if not self.samples:
            raise ValueError("rolling market window requires at least one sample")
        first = self.samples[0]
        previous_ts: int | None = None
        for sample in self.samples:
            if (
                sample.venue,
                sample.symbol,
                sample.base_asset,
                sample.quote_asset,
            ) != (
                first.venue,
                first.symbol,
                first.base_asset,
                first.quote_asset,
            ):
                raise ValueError("rolling window samples must belong to one exact market")
            if previous_ts is not None and sample.observed_at_ms <= previous_ts:
                raise ValueError("rolling window samples must have strictly increasing timestamps")
            previous_ts = sample.observed_at_ms

    @classmethod
    def from_quotes(
        cls,
        quotes: Iterable[QuoteSnapshot],
        *,
        policy: RollingWindowPolicy | None = None,
        end_ms: int | None = None,
    ) -> "RollingMarketWindow":
        active_policy = policy or RollingWindowPolicy()
        samples = [RollingMarketSample.from_quote(quote) for quote in quotes]
        if not samples:
            raise ValueError("at least one quote is required")
        for previous, current in zip(samples, samples[1:]):
            if current.observed_at_ms <= previous.observed_at_ms:
                raise ValueError("rolling-window input must be strictly timestamp ordered")
        effective_end = end_ms if end_ms is not None else samples[-1].observed_at_ms
        if effective_end < 0:
            raise ValueError("end_ms cannot be negative")
        if samples[-1].observed_at_ms > effective_end:
            raise ValueError("rolling-window sample cannot be in the future")
        cutoff = effective_end - active_policy.horizon_ms
        retained = tuple(sample for sample in samples if sample.observed_at_ms >= cutoff)
        if not retained:
            raise ValueError("no samples remain inside rolling horizon")
        return cls(policy=active_policy, samples=retained)

    def canonical_payload(self) -> dict[str, Any]:
        return {
            "schema": "resonance.arbitrage.rolling-window/v0.1",
            "policy": asdict(self.policy),
            "samples": [sample.to_payload() for sample in self.samples],
        }

    def canonical_json(self) -> str:
        return json.dumps(
            self.canonical_payload(),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )

    @property
    def sha256(self) -> str:
        return hashlib.sha256(self.canonical_json().encode("utf-8")).hexdigest()

    def summary(self, *, evaluation_time_ms: int | None = None) -> RollingWindowSummary:
        first = self.samples[0]
        end_ms = self.samples[-1].observed_at_ms
        evaluation_time = end_ms if evaluation_time_ms is None else evaluation_time_ms
        if evaluation_time < end_ms:
            raise ValueError("evaluation_time_ms cannot precede latest rolling sample")

        start_ms = first.observed_at_ms
        observed_span = end_ms - start_ms
        coverage_ratio = min(1.0, observed_span / self.policy.horizon_ms)
        reasons: list[str] = []
        if len(self.samples) < self.policy.min_samples:
            reasons.append("insufficient_sample_count")
        if coverage_ratio < self.policy.min_coverage_ratio:
            reasons.append("insufficient_time_coverage")

        returns_bps = [
            (current.mid_price / previous.mid_price - 1.0) * 10_000.0
            for previous, current in zip(self.samples, self.samples[1:])
        ]
        volatility = pstdev(returns_bps) if len(returns_bps) >= 2 else None
        if volatility is None:
            reasons.append("insufficient_return_observations")

        spreads = [sample.spread_bps for sample in self.samples]
        notionals = [sample.top_book_notional_quote for sample in self.samples]
        ages = [
            max(0, evaluation_time - sample.freshness_reference_ms)
            for sample in self.samples
        ]

        return RollingWindowSummary(
            venue=first.venue,
            symbol=first.symbol,
            base_asset=first.base_asset,
            quote_asset=first.quote_asset,
            start_ms=start_ms,
            end_ms=end_ms,
            horizon_ms=self.policy.horizon_ms,
            sample_count=len(self.samples),
            coverage_ratio=coverage_ratio,
            short_window_return_volatility_bps=volatility,
            max_spread_bps=max(spreads),
            mean_spread_bps=sum(spreads) / len(spreads),
            min_top_book_notional_quote=min(notionals),
            max_quote_age_ms=max(ages),
            quote_age_dispersion_ms=max(ages) - min(ages),
            complete=not reasons,
            reasons=tuple(reasons),
        )
