from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass, replace
from enum import Enum
import hashlib
import hmac
import json
import math
from statistics import mean
from types import MappingProxyType
from typing import Any

from .engine import Policy, evaluate_route
from .model import Edge, Verdict
from .observation import OutcomeClass, classify_outcome
from .quotes import CostAssumption, QuoteSnapshot, quote_to_trade_edges
from .regime import MarketRegime, RegimePolicy
from .rolling_state import RollingMarketSample, RollingMarketWindow, RollingWindowPolicy
from .window_regime import derive_window_regime_context


_REPLAY_CASE_SCHEMA = "resonance.arbitrage.replay-case/v0.1"
_REPLAY_BUNDLE_SCHEMA = "resonance.arbitrage.replay-bundle/v0.1"
_REPLAY_REPORT_SCHEMA = "resonance.arbitrage.replay-report/v0.1"


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


class ReplaySide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


@dataclass(frozen=True, slots=True)
class ReplayLeg:
    snapshot_index: int
    side: ReplaySide
    costs: CostAssumption

    def __post_init__(self) -> None:
        if self.snapshot_index < 0:
            raise ValueError("snapshot_index must be non-negative")
        if not isinstance(self.side, ReplaySide):
            raise ValueError("side must be ReplaySide")
        if not isinstance(self.costs, CostAssumption):
            raise ValueError("costs must be CostAssumption")

    def to_payload(self) -> dict[str, Any]:
        return {
            "snapshot_index": self.snapshot_index,
            "side": self.side.value,
            "costs": asdict(self.costs),
        }


@dataclass(frozen=True, slots=True)
class ReplayOutcome:
    observed_at_ms: int
    realized_net_edge_bps: float | None = None
    expired: bool = False

    def __post_init__(self) -> None:
        if self.observed_at_ms < 0:
            raise ValueError("observed_at_ms cannot be negative")
        if self.realized_net_edge_bps is not None and not math.isfinite(self.realized_net_edge_bps):
            raise ValueError("realized_net_edge_bps must be finite when supplied")
        if self.expired and self.realized_net_edge_bps is not None:
            raise ValueError("expired replay outcome cannot have realized edge")

    @property
    def terminal(self) -> bool:
        return self.expired or self.realized_net_edge_bps is not None


@dataclass(frozen=True, slots=True)
class ReplayCase:
    case_id: str
    logical_operation_id: str
    attempt: int
    detected_at_ms: int
    evaluation_time_ms: int
    start_amount: float
    snapshots: tuple[QuoteSnapshot, ...]
    windows_by_market: Mapping[str, RollingMarketWindow]
    legs: tuple[ReplayLeg, ...]
    engine_policy: Policy
    regime_policy: RegimePolicy
    outcome: ReplayOutcome

    def __post_init__(self) -> None:
        object.__setattr__(self, "snapshots", tuple(self.snapshots))
        object.__setattr__(self, "legs", tuple(self.legs))
        object.__setattr__(
            self,
            "windows_by_market",
            MappingProxyType(dict(self.windows_by_market)),
        )

        if not self.case_id or not self.logical_operation_id:
            raise ValueError("case_id and logical_operation_id must be non-empty")
        if self.attempt < 1:
            raise ValueError("attempt must be >= 1")
        if self.detected_at_ms < 0 or self.evaluation_time_ms < 0:
            raise ValueError("replay timestamps cannot be negative")
        if self.detected_at_ms > self.evaluation_time_ms:
            raise ValueError("detected_at_ms cannot follow evaluation_time_ms")
        if self.outcome.observed_at_ms < self.evaluation_time_ms:
            raise ValueError("paper outcome cannot precede replay evaluation")
        if not math.isfinite(self.start_amount) or self.start_amount <= 0:
            raise ValueError("start_amount must be finite and positive")
        if not self.snapshots or not self.legs:
            raise ValueError("replay case requires snapshots and route legs")
        if not isinstance(self.engine_policy, Policy) or not isinstance(self.regime_policy, RegimePolicy):
            raise ValueError("replay policies have invalid types")

        for snapshot in self.snapshots:
            if not isinstance(snapshot, QuoteSnapshot):
                raise ValueError("snapshots must contain QuoteSnapshot values")
            if snapshot.observed_at_ms > self.evaluation_time_ms:
                raise ValueError("future quote observation cannot enter replay decision")
            if snapshot.freshness_reference_ms > self.evaluation_time_ms:
                raise ValueError("future quote provenance cannot enter replay decision")

        for key, window in self.windows_by_market.items():
            if not key or not isinstance(window, RollingMarketWindow):
                raise ValueError("windows_by_market must contain named RollingMarketWindow values")
            if any(sample.observed_at_ms > self.evaluation_time_ms for sample in window.samples):
                raise ValueError("future rolling sample cannot enter replay decision")
            if any(sample.freshness_reference_ms > self.evaluation_time_ms for sample in window.samples):
                raise ValueError("future rolling provenance cannot enter replay decision")

        for leg in self.legs:
            if not isinstance(leg, ReplayLeg):
                raise ValueError("legs must contain ReplayLeg values")
            if leg.snapshot_index >= len(self.snapshots):
                raise ValueError("route leg snapshot_index is out of range")

        self.build_route()
        _canonical_json(self.canonical_payload())

    def build_route(self) -> tuple[Edge, ...]:
        edges: list[Edge] = []
        for leg in self.legs:
            buy, sell = quote_to_trade_edges(
                self.snapshots[leg.snapshot_index],
                leg.costs,
                now_ms=self.evaluation_time_ms,
            )
            edges.append(buy if leg.side is ReplaySide.BUY else sell)
        for previous, current in zip(edges, edges[1:]):
            if previous.dst != current.src:
                raise ValueError("replay route legs are not causally continuous")
        return tuple(edges)

    @property
    def route_id(self) -> str:
        semantic_legs = []
        for leg in self.legs:
            snapshot = self.snapshots[leg.snapshot_index]
            semantic_legs.append(
                {
                    "venue": snapshot.venue,
                    "symbol": snapshot.symbol,
                    "base_asset": snapshot.base_asset,
                    "quote_asset": snapshot.quote_asset,
                    "side": leg.side.value,
                    "costs": asdict(leg.costs),
                }
            )
        return _sha256({"route": semantic_legs})

    @property
    def decision_fingerprint(self) -> str:
        payload = self.canonical_payload()
        for key in ("case_id", "logical_operation_id", "attempt", "outcome"):
            payload.pop(key, None)
        return _sha256(payload)

    def canonical_payload(self) -> dict[str, Any]:
        return {
            "schema": _REPLAY_CASE_SCHEMA,
            "case_id": self.case_id,
            "logical_operation_id": self.logical_operation_id,
            "attempt": self.attempt,
            "detected_at_ms": self.detected_at_ms,
            "evaluation_time_ms": self.evaluation_time_ms,
            "start_amount": self.start_amount,
            "snapshots": [asdict(snapshot) for snapshot in self.snapshots],
            "windows_by_market": {
                key: self.windows_by_market[key].canonical_payload()
                for key in sorted(self.windows_by_market)
            },
            "legs": [leg.to_payload() for leg in self.legs],
            "engine_policy": asdict(self.engine_policy),
            "regime_policy": asdict(self.regime_policy),
            "outcome": asdict(self.outcome),
        }

    @property
    def sha256(self) -> str:
        return _sha256(self.canonical_payload())

    @classmethod
    def from_payload(cls, payload: Mapping[str, Any]) -> "ReplayCase":
        if payload.get("schema") != _REPLAY_CASE_SCHEMA:
            raise ValueError("unsupported replay case schema")
        try:
            snapshots = tuple(QuoteSnapshot(**item) for item in payload["snapshots"])
            windows: dict[str, RollingMarketWindow] = {}
            for key, raw_window in payload["windows_by_market"].items():
                if raw_window.get("schema") != "resonance.arbitrage.rolling-window/v0.1":
                    raise ValueError("unsupported rolling-window schema in replay case")
                windows[key] = RollingMarketWindow(
                    policy=RollingWindowPolicy(**raw_window["policy"]),
                    samples=tuple(RollingMarketSample(**sample) for sample in raw_window["samples"]),
                )
            legs = tuple(
                ReplayLeg(
                    snapshot_index=item["snapshot_index"],
                    side=ReplaySide(item["side"]),
                    costs=CostAssumption(**item["costs"]),
                )
                for item in payload["legs"]
            )
            case = cls(
                case_id=payload["case_id"],
                logical_operation_id=payload["logical_operation_id"],
                attempt=payload["attempt"],
                detected_at_ms=payload["detected_at_ms"],
                evaluation_time_ms=payload["evaluation_time_ms"],
                start_amount=payload["start_amount"],
                snapshots=snapshots,
                windows_by_market=windows,
                legs=legs,
                engine_policy=Policy(**payload["engine_policy"]),
                regime_policy=RegimePolicy(**payload["regime_policy"]),
                outcome=ReplayOutcome(**payload["outcome"]),
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError("invalid replay case payload") from exc
        if case.canonical_payload() != dict(payload):
            raise ValueError("replay case payload is not canonical")
        return case


@dataclass(frozen=True, slots=True)
class ReplayBundle:
    cases: tuple[ReplayCase, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "cases", tuple(self.cases))
        if not self.cases:
            raise ValueError("replay bundle requires at least one case")
        case_ids: set[str] = set()
        grouped: dict[str, list[ReplayCase]] = defaultdict(list)
        for case in self.cases:
            if not isinstance(case, ReplayCase):
                raise ValueError("replay bundle cases must be ReplayCase values")
            if case.case_id in case_ids:
                raise ValueError("duplicate replay case_id")
            case_ids.add(case.case_id)
            grouped[case.logical_operation_id].append(case)

        for operation_id, rows in grouped.items():
            ordered = sorted(rows, key=lambda item: item.attempt)
            attempts = [row.attempt for row in ordered]
            if attempts != list(range(1, len(ordered) + 1)):
                raise ValueError(f"replay attempts must be contiguous for {operation_id}")
            fingerprint = ordered[0].decision_fingerprint
            detected_at = ordered[0].detected_at_ms
            for index, row in enumerate(ordered):
                if row.decision_fingerprint != fingerprint or row.detected_at_ms != detected_at:
                    raise ValueError("logical replay operation drifted across attempts")
                if index < len(ordered) - 1 and row.outcome.terminal:
                    raise ValueError("terminal replay outcome cannot be retried")

    def collapsed_cases(self) -> tuple[ReplayCase, ...]:
        latest: dict[str, ReplayCase] = {}
        for case in self.cases:
            current = latest.get(case.logical_operation_id)
            if current is None or case.attempt > current.attempt:
                latest[case.logical_operation_id] = case
        return tuple(
            sorted(
                latest.values(),
                key=lambda row: (row.detected_at_ms, row.logical_operation_id),
            )
        )

    def canonical_payload(self) -> dict[str, Any]:
        return {
            "schema": _REPLAY_BUNDLE_SCHEMA,
            "cases": [case.canonical_payload() for case in self.cases],
        }

    @property
    def sha256(self) -> str:
        return _sha256(self.canonical_payload())

    def to_envelope(self) -> dict[str, Any]:
        return {"payload": self.canonical_payload(), "sha256": self.sha256}

    @classmethod
    def from_envelope(cls, envelope: Mapping[str, Any]) -> "ReplayBundle":
        try:
            payload = envelope["payload"]
            supplied_sha = envelope["sha256"]
        except KeyError as exc:
            raise ValueError("replay bundle envelope is incomplete") from exc
        if not isinstance(payload, dict) or not isinstance(supplied_sha, str):
            raise ValueError("replay bundle envelope has invalid types")
        digest = _sha256(payload)
        if not hmac.compare_digest(digest, supplied_sha):
            raise ValueError("replay bundle SHA-256 does not match payload")
        if payload.get("schema") != _REPLAY_BUNDLE_SCHEMA:
            raise ValueError("unsupported replay bundle schema")
        try:
            bundle = cls(cases=tuple(ReplayCase.from_payload(item) for item in payload["cases"]))
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError("invalid replay bundle payload") from exc
        if bundle.canonical_payload() != payload:
            raise ValueError("replay bundle payload is not canonical")
        if not hmac.compare_digest(bundle.sha256, supplied_sha):
            raise ValueError("reconstructed replay bundle digest mismatch")
        return bundle


@dataclass(frozen=True, slots=True)
class ReplayResult:
    case_id: str
    logical_operation_id: str
    attempt: int
    route_id: str
    case_sha256: str
    regime: MarketRegime
    expected_verdict: Verdict
    expected_edge_bps: float
    required_edge_bps: float
    observed_edge_bps: float | None
    outcome_class: OutcomeClass
    reasons: tuple[str, ...]

    @property
    def prediction_error_bps(self) -> float | None:
        if self.observed_edge_bps is None:
            return None
        return self.observed_edge_bps - self.expected_edge_bps

    def to_payload(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "logical_operation_id": self.logical_operation_id,
            "attempt": self.attempt,
            "route_id": self.route_id,
            "case_sha256": self.case_sha256,
            "regime": self.regime.value,
            "expected_verdict": self.expected_verdict.value,
            "expected_edge_bps": self.expected_edge_bps,
            "required_edge_bps": self.required_edge_bps,
            "observed_edge_bps": self.observed_edge_bps,
            "outcome_class": self.outcome_class.value,
            "reasons": list(self.reasons),
            "prediction_error_bps": self.prediction_error_bps,
        }


def replay_case(
    case: ReplayCase,
    *,
    engine_policy: Policy | None = None,
    regime_policy: RegimePolicy | None = None,
) -> ReplayResult:
    active_engine_policy = engine_policy or case.engine_policy
    active_regime_policy = regime_policy or case.regime_policy
    route = case.build_route()
    expected = evaluate_route(route, case.start_amount, policy=active_engine_policy)
    context = derive_window_regime_context(
        route,
        case.snapshots,
        windows_by_market=case.windows_by_market,
        evaluation_time_ms=case.evaluation_time_ms,
        start_amount=case.start_amount,
        regime_policy=active_regime_policy,
    )
    required_edge_bps = active_engine_policy.execute_net_edge * 10_000.0
    reasons = list(expected.reasons)

    if context.classification.regime is MarketRegime.UNKNOWN and expected.verdict is not Verdict.REJECT:
        outcome_class = OutcomeClass.INDETERMINATE
        reasons.append("REGIME_EVIDENCE_UNKNOWN")
    else:
        outcome_class = classify_outcome(
            expected_verdict=expected.verdict.value,
            observed_edge_bps=case.outcome.realized_net_edge_bps,
            required_edge_bps=required_edge_bps,
            expired=case.outcome.expired,
        )

    return ReplayResult(
        case_id=case.case_id,
        logical_operation_id=case.logical_operation_id,
        attempt=case.attempt,
        route_id=case.route_id,
        case_sha256=case.sha256,
        regime=context.classification.regime,
        expected_verdict=expected.verdict,
        expected_edge_bps=expected.net_edge * 10_000.0,
        required_edge_bps=required_edge_bps,
        observed_edge_bps=case.outcome.realized_net_edge_bps,
        outcome_class=outcome_class,
        reasons=tuple(reasons),
    )


@dataclass(frozen=True, slots=True)
class ReplayMetrics:
    logical_operations: int
    true_positive: int
    false_positive: int
    expired: int
    rejected: int
    indeterminate: int
    opportunity_truth_rate: float | None
    false_opportunity_rate: float | None
    route_survival_rate: float | None
    mean_prediction_error_bps: float | None

    def to_payload(self) -> dict[str, Any]:
        return asdict(self)


def calculate_replay_metrics(results: Sequence[ReplayResult]) -> ReplayMetrics:
    counts = {outcome: 0 for outcome in OutcomeClass}
    errors: list[float] = []
    for result in results:
        counts[result.outcome_class] += 1
        error = result.prediction_error_bps
        if error is not None and result.outcome_class in {
            OutcomeClass.TRUE_POSITIVE,
            OutcomeClass.FALSE_POSITIVE,
        }:
            errors.append(error)

    truth_population = counts[OutcomeClass.TRUE_POSITIVE] + counts[OutcomeClass.FALSE_POSITIVE]
    survival_population = truth_population + counts[OutcomeClass.EXPIRED]
    return ReplayMetrics(
        logical_operations=len(results),
        true_positive=counts[OutcomeClass.TRUE_POSITIVE],
        false_positive=counts[OutcomeClass.FALSE_POSITIVE],
        expired=counts[OutcomeClass.EXPIRED],
        rejected=counts[OutcomeClass.REJECTED],
        indeterminate=counts[OutcomeClass.INDETERMINATE],
        opportunity_truth_rate=(counts[OutcomeClass.TRUE_POSITIVE] / truth_population if truth_population else None),
        false_opportunity_rate=(counts[OutcomeClass.FALSE_POSITIVE] / truth_population if truth_population else None),
        route_survival_rate=(truth_population / survival_population if survival_population else None),
        mean_prediction_error_bps=mean(errors) if errors else None,
    )


@dataclass(frozen=True, slots=True)
class CalibrationSlice:
    key: str
    metrics: ReplayMetrics

    def to_payload(self) -> dict[str, Any]:
        return {"key": self.key, "metrics": self.metrics.to_payload()}


@dataclass(frozen=True, slots=True)
class CalibrationReport:
    bundle_sha256: str
    results: tuple[ReplayResult, ...]
    overall: ReplayMetrics
    by_regime: tuple[CalibrationSlice, ...]
    by_route: tuple[CalibrationSlice, ...]

    def canonical_payload(self) -> dict[str, Any]:
        return {
            "schema": _REPLAY_REPORT_SCHEMA,
            "bundle_sha256": self.bundle_sha256,
            "results": [result.to_payload() for result in self.results],
            "overall": self.overall.to_payload(),
            "by_regime": [item.to_payload() for item in self.by_regime],
            "by_route": [item.to_payload() for item in self.by_route],
            "advisory_only": True,
        }

    @property
    def sha256(self) -> str:
        return _sha256(self.canonical_payload())

    def to_envelope(self) -> dict[str, Any]:
        return {"payload": self.canonical_payload(), "sha256": self.sha256}


def benchmark_bundle(bundle: ReplayBundle) -> CalibrationReport:
    results = tuple(replay_case(case) for case in bundle.collapsed_cases())
    regime_groups: dict[str, list[ReplayResult]] = defaultdict(list)
    route_groups: dict[str, list[ReplayResult]] = defaultdict(list)
    for result in results:
        regime_groups[result.regime.value].append(result)
        route_groups[result.route_id].append(result)
    by_regime = tuple(
        CalibrationSlice(key=key, metrics=calculate_replay_metrics(regime_groups[key]))
        for key in sorted(regime_groups)
    )
    by_route = tuple(
        CalibrationSlice(key=key, metrics=calculate_replay_metrics(route_groups[key]))
        for key in sorted(route_groups)
    )
    return CalibrationReport(
        bundle_sha256=bundle.sha256,
        results=results,
        overall=calculate_replay_metrics(results),
        by_regime=by_regime,
        by_route=by_route,
    )


@dataclass(frozen=True, slots=True)
class SensitivityPoint:
    execute_net_edge_bps: float
    volatile_return_bps: float
    metrics: ReplayMetrics
    execute_sim_count: int
    regime_counts: dict[str, int]

    def to_payload(self) -> dict[str, Any]:
        return {
            "execute_net_edge_bps": self.execute_net_edge_bps,
            "volatile_return_bps": self.volatile_return_bps,
            "metrics": self.metrics.to_payload(),
            "execute_sim_count": self.execute_sim_count,
            "regime_counts": {key: self.regime_counts[key] for key in sorted(self.regime_counts)},
            "advisory_only": True,
        }


def threshold_sensitivity(
    bundle: ReplayBundle,
    *,
    execute_net_edge_bps: Sequence[float],
    volatile_return_bps: Sequence[float],
) -> tuple[SensitivityPoint, ...]:
    if not execute_net_edge_bps or not volatile_return_bps:
        raise ValueError("threshold sensitivity requires non-empty threshold grids")
    for value in (*execute_net_edge_bps, *volatile_return_bps):
        if not math.isfinite(value) or value < 0:
            raise ValueError("sensitivity thresholds must be finite and non-negative")

    collapsed = bundle.collapsed_cases()
    points: list[SensitivityPoint] = []
    for execute_bps in sorted(set(execute_net_edge_bps)):
        for volatile_bps in sorted(set(volatile_return_bps)):
            results: list[ReplayResult] = []
            for case in collapsed:
                engine_policy = replace(
                    case.engine_policy,
                    execute_net_edge=execute_bps / 10_000.0,
                )
                if engine_policy.execute_net_edge <= engine_policy.observe_net_edge:
                    raise ValueError("sensitivity execute threshold must exceed observe threshold")
                regime_policy = replace(
                    case.regime_policy,
                    volatile_return_bps=volatile_bps,
                )
                results.append(
                    replay_case(
                        case,
                        engine_policy=engine_policy,
                        regime_policy=regime_policy,
                    )
                )
            regime_counts: dict[str, int] = defaultdict(int)
            for result in results:
                regime_counts[result.regime.value] += 1
            points.append(
                SensitivityPoint(
                    execute_net_edge_bps=execute_bps,
                    volatile_return_bps=volatile_bps,
                    metrics=calculate_replay_metrics(results),
                    execute_sim_count=sum(
                        result.expected_verdict is Verdict.EXECUTE_SIM
                        for result in results
                    ),
                    regime_counts=dict(regime_counts),
                )
            )
    return tuple(points)
