from __future__ import annotations

from dataclasses import dataclass
import math

from .model import Edge, Node
from .validation import require_non_negative


@dataclass(frozen=True, slots=True)
class QuoteSnapshot:
    """Normalized best-bid/best-ask snapshot from a public market-data source."""

    venue: str
    symbol: str
    base_asset: str
    quote_asset: str
    bid_price: float
    bid_qty: float
    ask_price: float
    ask_qty: float
    observed_at_ms: int
    source_url: str
    timestamp_class: str = "client_observed"
    source_timestamp_ms: int | None = None

    def __post_init__(self) -> None:
        for name in ("venue", "symbol", "base_asset", "quote_asset", "source_url", "timestamp_class"):
            if not getattr(self, name):
                raise ValueError(f"{name} must be non-empty")

        for name, value in (
            ("bid_price", self.bid_price),
            ("bid_qty", self.bid_qty),
            ("ask_price", self.ask_price),
            ("ask_qty", self.ask_qty),
        ):
            if not math.isfinite(value) or value <= 0:
                raise ValueError(f"{name} must be finite and positive")

        if self.observed_at_ms < 0:
            raise ValueError("observed_at_ms cannot be negative")
        if self.source_timestamp_ms is not None and self.source_timestamp_ms < 0:
            raise ValueError("source_timestamp_ms cannot be negative")

    @property
    def freshness_reference_ms(self) -> int:
        return self.source_timestamp_ms if self.source_timestamp_ms is not None else self.observed_at_ms

    def age_ms(self, now_ms: int) -> int:
        if now_ms < 0:
            raise ValueError("now_ms cannot be negative")
        return max(0, now_ms - self.freshness_reference_ms)


@dataclass(frozen=True, slots=True)
class CostAssumption:
    """Explicit paper-model costs. These are caller supplied, never inferred from account tier."""

    fee_bps: float
    slippage_bps: float
    gas_bps: float = 0.0

    def __post_init__(self) -> None:
        for name, value in (
            ("fee_bps", self.fee_bps),
            ("slippage_bps", self.slippage_bps),
            ("gas_bps", self.gas_bps),
        ):
            if not math.isfinite(value):
                raise ValueError(f"{name} must be finite")
            require_non_negative(name, value)
        if self.fee_bps + self.slippage_bps + self.gas_bps >= 10_000:
            raise ValueError("combined costs must be below 100%")


def quote_to_trade_edges(
    quote: QuoteSnapshot,
    costs: CostAssumption,
    *,
    now_ms: int,
) -> tuple[Edge, Edge]:
    """Convert top-of-book data into buy and sell graph edges.

    BUY: quote asset -> base asset at ask, capacity expressed in quote asset.
    SELL: base asset -> quote asset at bid, capacity expressed in base asset.
    """

    quote_age_ms = quote.age_ms(now_ms)
    base = Node(quote.venue, quote.base_asset)
    counter = Node(quote.venue, quote.quote_asset)

    buy = Edge(
        src=counter,
        dst=base,
        rate=1.0 / quote.ask_price,
        fee_bps=costs.fee_bps,
        slippage_bps=costs.slippage_bps,
        gas_bps=costs.gas_bps,
        capacity=quote.ask_price * quote.ask_qty,
        quote_age_ms=quote_age_ms,
    )
    sell = Edge(
        src=base,
        dst=counter,
        rate=quote.bid_price,
        fee_bps=costs.fee_bps,
        slippage_bps=costs.slippage_bps,
        gas_bps=costs.gas_bps,
        capacity=quote.bid_qty,
        quote_age_ms=quote_age_ms,
    )
    return buy, sell
