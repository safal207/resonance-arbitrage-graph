from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import hashlib
import json
import math
from typing import Any

from .real_market_corpus import RealMarketReplayCorpus
from .replay import ReplayCase, replay_case


_POLICY_SCHEMA = "resonance.arbitrage.corpus-quality-policy/v0.1"
_REPORT_SCHEMA = "resonance.arbitrage.corpus-quality-report/v0.1"


def _canonical_json(payload: Any) -> str:
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def _sha256(payload: Any) -> str:
    return hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()


def _effective_count(counts: Counter[Any]) -> float:
    total = sum(counts.values())
    if total <= 0:
        return 0.0
    concentration = sum((count / total) ** 2 for count in counts.values())
    return 1.0 / concentration


def _largest_share(counts: Counter[Any]) -> float:
    total = sum(counts.values())
    if total <= 0:
        return 0.0
    return max(counts.values()) / total


def _route_topology_id(case: ReplayCase) -> str:
    """Hash route topology without allowing fee-policy churn to fake diversity."""
    legs: list[dict[str, str]] = []
    for leg in case.legs:
        snapshot = case.snapshots[leg.snapshot_index]
        legs.append(
            {
                "venue": snapshot.venue,
                "symbol": snapshot.symbol,
                "base_asset": snapshot.base_asset,
                "quote_asset": snapshot.quote_asset,
                "side": leg.side.value,
            }
        )
    return _sha256({"route_topology": legs})


def _route_market_identity(case: ReplayCase, snapshot_index: int) -> str:
    snapshot = case.snapshots[snapshot_index]
    return (
        f"{snapshot.venue}:{snapshot.symbol}:"
        f"{snapshot.base_asset}/{snapshot.quote_asset}"
    )


def _terminal_cases(corpus: RealMarketReplayCorpus) -> tuple[ReplayCase, ...]:
    latest: dict[str, ReplayCase] = {}
    for record in corpus.records:
        case = record.replay_case
        current = latest.get(case.logical_operation_id)
        if current is None or case.attempt > current.attempt:
            latest[case.logical_operation_id] = case
    return tuple(
        case
        for case in sorted(
            latest.values(),
            key=lambda item: (item.evaluation_time_ms, item.logical_operation_id),
        )
        if case.outcome.terminal
    )


@dataclass(frozen=True, slots=True)
class CorpusQualityPolicy:
    min_decision_batches: int = 20
    min_effective_decision_batches: float = 10.0
    min_temporal_span_ms: int = 3_600_000
    min_distinct_routes: int = 3
    min_effective_routes: float = 2.0
    min_distinct_route_markets: int = 3
    min_distinct_regimes: int = 2

    def __post_init__(self) -> None:
        for name in (
            "min_decision_batches",
            "min_distinct_routes",
            "min_distinct_route_markets",
            "min_distinct_regimes",
        ):
            if getattr(self, name) < 1:
                raise ValueError(f"{name} must be >= 1")
        if self.min_temporal_span_ms < 0:
            raise ValueError("min_temporal_span_ms must be non-negative")
        for name in (
            "min_effective_decision_batches",
            "min_effective_routes",
        ):
            value = getattr(self, name)
            if not math.isfinite(value) or value < 1.0:
                raise ValueError(f"{name} must be finite and >= 1")
        if self.min_effective_decision_batches > self.min_decision_batches:
            raise ValueError(
                "min_effective_decision_batches cannot exceed min_decision_batches"
            )
        if self.min_effective_routes > self.min_distinct_routes:
            raise ValueError("min_effective_routes cannot exceed min_distinct_routes")

    def to_payload(self) -> dict[str, Any]:
        return {
            "schema": _POLICY_SCHEMA,
            "min_decision_batches": self.min_decision_batches,
            "min_effective_decision_batches": self.min_effective_decision_batches,
            "min_temporal_span_ms": self.min_temporal_span_ms,
            "min_distinct_routes": self.min_distinct_routes,
            "min_effective_routes": self.min_effective_routes,
            "min_distinct_route_markets": self.min_distinct_route_markets,
            "min_distinct_regimes": self.min_distinct_regimes,
            "interpretation": "RESEARCH_READINESS_ONLY",
        }

    @property
    def sha256(self) -> str:
        return _sha256(self.to_payload())


@dataclass(frozen=True, slots=True)
class CorpusQualityReport:
    corpus_sha256: str
    policy_sha256: str
    terminal_operation_count: int
    decision_batch_counts: tuple[tuple[int, int], ...]
    effective_decision_batches: float
    largest_decision_batch_share: float
    temporal_span_ms: int
    route_topology_counts: tuple[tuple[str, int], ...]
    effective_routes: float
    largest_route_share: float
    route_market_identities: tuple[str, ...]
    regime_counts: tuple[tuple[str, int], ...]
    failed_dimensions: tuple[str, ...]
    quality_ready: bool
    paper_only: bool = True
    public_market_data_only: bool = True

    def __post_init__(self) -> None:
        if self.terminal_operation_count < 0:
            raise ValueError("terminal_operation_count cannot be negative")
        if self.temporal_span_ms < 0:
            raise ValueError("temporal_span_ms cannot be negative")
        for value_name in (
            "effective_decision_batches",
            "effective_routes",
            "largest_decision_batch_share",
            "largest_route_share",
        ):
            value = getattr(self, value_name)
            if not math.isfinite(value) or value < 0:
                raise ValueError(f"{value_name} must be finite and non-negative")
        for share_name in (
            "largest_decision_batch_share",
            "largest_route_share",
        ):
            if getattr(self, share_name) > 1.0:
                raise ValueError(f"{share_name} cannot exceed 1")
        if self.quality_ready != (len(self.failed_dimensions) == 0):
            raise ValueError("quality_ready must match failed_dimensions")
        if self.paper_only is not True or self.public_market_data_only is not True:
            raise ValueError("corpus quality report must remain public-data paper-only")

    @property
    def distinct_decision_batches(self) -> int:
        return len(self.decision_batch_counts)

    @property
    def distinct_routes(self) -> int:
        return len(self.route_topology_counts)

    @property
    def distinct_route_markets(self) -> int:
        return len(self.route_market_identities)

    @property
    def distinct_regimes(self) -> int:
        return len(self.regime_counts)

    def to_payload(self) -> dict[str, Any]:
        return {
            "schema": _REPORT_SCHEMA,
            "corpus_sha256": self.corpus_sha256,
            "policy_sha256": self.policy_sha256,
            "terminal_operation_count": self.terminal_operation_count,
            "decision_batch_counts": [
                {"evaluation_time_ms": at_ms, "terminal_operations": count}
                for at_ms, count in self.decision_batch_counts
            ],
            "distinct_decision_batches": self.distinct_decision_batches,
            "effective_decision_batches": self.effective_decision_batches,
            "largest_decision_batch_share": self.largest_decision_batch_share,
            "temporal_span_ms": self.temporal_span_ms,
            "route_topology_counts": [
                {"route_topology_id": route_id, "terminal_operations": count}
                for route_id, count in self.route_topology_counts
            ],
            "distinct_routes": self.distinct_routes,
            "effective_routes": self.effective_routes,
            "largest_route_share": self.largest_route_share,
            "route_market_identities": list(self.route_market_identities),
            "distinct_route_markets": self.distinct_route_markets,
            "regime_counts": [
                {"regime": regime, "terminal_operations": count}
                for regime, count in self.regime_counts
            ],
            "distinct_regimes": self.distinct_regimes,
            "failed_dimensions": list(self.failed_dimensions),
            "quality_ready": self.quality_ready,
            "paper_only": self.paper_only,
            "public_market_data_only": self.public_market_data_only,
            "interpretation": "RESEARCH_READINESS_ONLY",
        }

    @property
    def sha256(self) -> str:
        return _sha256(self.to_payload())


def build_corpus_quality_report(
    corpus: RealMarketReplayCorpus,
    *,
    policy: CorpusQualityPolicy | None = None,
) -> CorpusQualityReport:
    policy = policy or CorpusQualityPolicy()
    terminal = _terminal_cases(corpus)

    batch_counts: Counter[int] = Counter(
        case.evaluation_time_ms for case in terminal
    )
    route_counts: Counter[str] = Counter()
    route_markets: set[str] = set()
    regime_counts: Counter[str] = Counter()

    for case in terminal:
        route_counts[_route_topology_id(case)] += 1
        for leg in case.legs:
            route_markets.add(_route_market_identity(case, leg.snapshot_index))
        regime_counts[replay_case(case).regime.value] += 1

    decision_times = sorted(batch_counts)
    temporal_span_ms = (
        decision_times[-1] - decision_times[0] if len(decision_times) >= 2 else 0
    )
    effective_batches = _effective_count(batch_counts)
    effective_routes = _effective_count(route_counts)

    failures: list[str] = []
    if len(batch_counts) < policy.min_decision_batches:
        failures.append("decision_batches")
    if effective_batches + 1e-12 < policy.min_effective_decision_batches:
        failures.append("effective_decision_batches")
    if temporal_span_ms < policy.min_temporal_span_ms:
        failures.append("temporal_span_ms")
    if len(route_counts) < policy.min_distinct_routes:
        failures.append("distinct_routes")
    if effective_routes + 1e-12 < policy.min_effective_routes:
        failures.append("effective_routes")
    if len(route_markets) < policy.min_distinct_route_markets:
        failures.append("distinct_route_markets")
    if len(regime_counts) < policy.min_distinct_regimes:
        failures.append("distinct_regimes")

    return CorpusQualityReport(
        corpus_sha256=corpus.sha256,
        policy_sha256=policy.sha256,
        terminal_operation_count=len(terminal),
        decision_batch_counts=tuple(sorted(batch_counts.items())),
        effective_decision_batches=effective_batches,
        largest_decision_batch_share=_largest_share(batch_counts),
        temporal_span_ms=temporal_span_ms,
        route_topology_counts=tuple(sorted(route_counts.items())),
        effective_routes=effective_routes,
        largest_route_share=_largest_share(route_counts),
        route_market_identities=tuple(sorted(route_markets)),
        regime_counts=tuple(sorted(regime_counts.items())),
        failed_dimensions=tuple(failures),
        quality_ready=not failures,
    )
