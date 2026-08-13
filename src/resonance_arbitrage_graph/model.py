from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import math


class Verdict(str, Enum):
    EXECUTE_SIM = "EXECUTE_SIM"
    OBSERVE = "OBSERVE"
    REJECT = "REJECT"


@dataclass(frozen=True, slots=True)
class Node:
    venue: str
    asset: str

    def __post_init__(self) -> None:
        if not self.venue or not self.asset:
            raise ValueError("venue and asset must be non-empty")

    @property
    def key(self) -> str:
        return f"{self.venue}:{self.asset}"


@dataclass(frozen=True, slots=True)
class Edge:
    src: Node
    dst: Node
    rate: float
    fee_bps: float = 0.0
    slippage_bps: float = 0.0
    gas_bps: float = 0.0
    capacity: float = math.inf
    latency_ms: int = 0
    quote_age_ms: int = 0
    failure_probability: float = 0.0
    settlement_probability: float = 1.0
    confidence: float = 1.0

    def __post_init__(self) -> None:
        if self.rate <= 0:
            raise ValueError("rate must be positive")
        if self.capacity <= 0:
            raise ValueError("capacity must be positive")
        if self.latency_ms < 0 or self.quote_age_ms < 0:
            raise ValueError("latency and quote age cannot be negative")
        for name, value in (
            ("failure_probability", self.failure_probability),
            ("settlement_probability", self.settlement_probability),
            ("confidence", self.confidence),
        ):
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be between 0 and 1")
        if self.total_cost_bps >= 10_000:
            raise ValueError("combined costs must be below 100%")

    @property
    def total_cost_bps(self) -> float:
        return self.fee_bps + self.slippage_bps + self.gas_bps

    @property
    def success_probability(self) -> float:
        return (
            (1.0 - self.failure_probability)
            * self.settlement_probability
            * self.confidence
        )

    def apply(self, amount: float, *, extra_slippage_bps: float = 0.0) -> float:
        if amount <= 0:
            raise ValueError("amount must be positive")
        if amount > self.capacity:
            raise ValueError("capacity exceeded")
        cost_bps = self.total_cost_bps + extra_slippage_bps
        if cost_bps >= 10_000:
            raise ValueError("combined execution costs must be below 100%")
        return amount * self.rate * (1.0 - cost_bps / 10_000.0)


@dataclass(frozen=True, slots=True)
class RouteResult:
    start_amount: float
    gross_final_amount: float
    final_amount: float
    gross_edge: float
    net_edge: float
    risk_adjusted_edge: float
    success_probability: float
    total_latency_ms: int
    verdict: Verdict
    reasons: tuple[str, ...]
