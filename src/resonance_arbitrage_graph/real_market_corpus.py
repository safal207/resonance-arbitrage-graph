from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass, replace
import hashlib
import hmac
import json
import math
from pathlib import Path
from typing import Any

from .engine import Policy, evaluate_route
from .model import Edge
from .quotes import CostAssumption, QuoteSnapshot, quote_to_trade_edges
from .regime import RegimePolicy
from .regime_gate import RegimeExecutionPolicy
from .replay import (
    ReplayBundle,
    ReplayCase,
    ReplayLeg,
    ReplayOutcome,
    ReplaySide,
)
from .rolling_state import RollingMarketWindow
from .scanner import ScannedOpportunity


_CORPUS_SCHEMA = "resonance.arbitrage.real-market-replay-corpus/v0.1"
_RECORD_SCHEMA = "resonance.arbitrage.real-market-replay-record/v0.1"
_ALLOWED_PHASES = {"DECISION", "OUTCOME"}


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


def _sha256_text(value: str, name: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise ValueError(f"{name} must be a lowercase SHA-256 digest")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{name} must be hexadecimal") from exc
    if value.lower() != value:
        raise ValueError(f"{name} must be lowercase")
    return value


def _market_identity(snapshot: QuoteSnapshot) -> tuple[str, str, str, str]:
    return (
        snapshot.venue,
        snapshot.symbol,
        snapshot.base_asset,
        snapshot.quote_asset,
    )


def route_to_replay_legs(
    route: Sequence[Edge],
    snapshots: Sequence[QuoteSnapshot],
    *,
    costs_by_venue: Mapping[str, CostAssumption],
    evaluation_time_ms: int,
) -> tuple[ReplayLeg, ...]:
    """Bind scanned graph edges back to their exact public quote snapshots."""
    legs: list[ReplayLeg] = []
    for route_edge in route:
        matches: list[ReplayLeg] = []
        for index, snapshot in enumerate(snapshots):
            try:
                costs = costs_by_venue[snapshot.venue]
            except KeyError as exc:
                raise ValueError(
                    f"missing explicit cost assumptions for venue: {snapshot.venue}"
                ) from exc
            buy, sell = quote_to_trade_edges(
                snapshot,
                costs,
                now_ms=evaluation_time_ms,
            )
            if buy == route_edge:
                matches.append(
                    ReplayLeg(
                        snapshot_index=index,
                        side=ReplaySide.BUY,
                        costs=costs,
                    )
                )
            if sell == route_edge:
                matches.append(
                    ReplayLeg(
                        snapshot_index=index,
                        side=ReplaySide.SELL,
                        costs=costs,
                    )
                )
        if len(matches) != 1:
            raise ValueError(
                "scanned route edge must map to exactly one decision-time quote"
            )
        legs.append(matches[0])
    return tuple(legs)


def build_decision_cases(
    snapshots: Sequence[QuoteSnapshot],
    windows_by_market: Mapping[str, RollingMarketWindow],
    opportunities: Sequence[ScannedOpportunity],
    *,
    costs_by_venue: Mapping[str, CostAssumption],
    evaluation_time_ms: int,
    start_amount: float,
    engine_policy: Policy | None = None,
    regime_policy: RegimePolicy | None = None,
    regime_execution_policy: RegimeExecutionPolicy | None = None,
    operation_prefix: str = "real-market",
) -> tuple[ReplayCase, ...]:
    snapshots = tuple(snapshots)
    if not snapshots:
        raise ValueError("decision capture requires public quote snapshots")
    if not opportunities:
        raise ValueError("decision capture requires at least one scanned opportunity")
    if evaluation_time_ms < 0:
        raise ValueError("evaluation_time_ms must be non-negative")
    if not math.isfinite(start_amount) or start_amount <= 0:
        raise ValueError("start_amount must be finite and positive")
    if not operation_prefix:
        raise ValueError("operation_prefix must be non-empty")

    active_engine_policy = engine_policy or Policy()
    active_regime_policy = regime_policy or RegimePolicy()
    active_gate_policy = regime_execution_policy or RegimeExecutionPolicy()

    cases: list[ReplayCase] = []
    for index, opportunity in enumerate(opportunities):
        operation_id = f"{operation_prefix}-{evaluation_time_ms}-{index}"
        legs = route_to_replay_legs(
            opportunity.route,
            snapshots,
            costs_by_venue=costs_by_venue,
            evaluation_time_ms=evaluation_time_ms,
        )
        cases.append(
            ReplayCase(
                case_id=f"{operation_id}:attempt:1",
                logical_operation_id=operation_id,
                attempt=1,
                detected_at_ms=evaluation_time_ms,
                evaluation_time_ms=evaluation_time_ms,
                start_amount=start_amount,
                snapshots=snapshots,
                windows_by_market=dict(windows_by_market),
                legs=legs,
                engine_policy=active_engine_policy,
                regime_policy=active_regime_policy,
                regime_execution_policy=active_gate_policy,
                outcome=ReplayOutcome(observed_at_ms=evaluation_time_ms),
            )
        )
    return tuple(cases)


def _outcome_route(
    case: ReplayCase,
    outcome_snapshots: Sequence[QuoteSnapshot],
    *,
    observed_at_ms: int,
) -> tuple[Edge, ...]:
    by_market: dict[tuple[str, str, str, str], list[QuoteSnapshot]] = {}
    for snapshot in outcome_snapshots:
        by_market.setdefault(_market_identity(snapshot), []).append(snapshot)

    edges: list[Edge] = []
    for leg in case.legs:
        decision_snapshot = case.snapshots[leg.snapshot_index]
        matches = by_market.get(_market_identity(decision_snapshot), [])
        if len(matches) != 1:
            raise ValueError(
                "outcome capture requires exactly one fresh quote for every route market"
            )
        buy, sell = quote_to_trade_edges(
            matches[0],
            leg.costs,
            now_ms=observed_at_ms,
        )
        edges.append(buy if leg.side is ReplaySide.BUY else sell)
    return tuple(edges)


def realized_future_edge_bps(
    case: ReplayCase,
    outcome_snapshots: Sequence[QuoteSnapshot],
    *,
    observed_at_ms: int,
) -> float:
    if observed_at_ms < case.evaluation_time_ms:
        raise ValueError("outcome observation cannot precede the decision")
    route = _outcome_route(
        case,
        outcome_snapshots,
        observed_at_ms=observed_at_ms,
    )
    result = evaluate_route(route, case.start_amount, policy=case.engine_policy)
    return result.net_edge * 10_000.0


def resolve_replay_case(
    case: ReplayCase,
    outcome_snapshots: Sequence[QuoteSnapshot],
    *,
    observed_at_ms: int,
) -> ReplayCase:
    if case.outcome.terminal:
        raise ValueError("cannot resolve an already terminal replay case")
    realized_edge_bps = realized_future_edge_bps(
        case,
        outcome_snapshots,
        observed_at_ms=observed_at_ms,
    )
    next_attempt = case.attempt + 1
    return replace(
        case,
        case_id=f"{case.logical_operation_id}:attempt:{next_attempt}",
        attempt=next_attempt,
        outcome=ReplayOutcome(
            observed_at_ms=observed_at_ms,
            realized_net_edge_bps=realized_edge_bps,
        ),
    )


@dataclass(frozen=True, slots=True)
class RealMarketReplayRecord:
    sequence: int
    previous_record_sha256: str | None
    phase: str
    captured_at_ms: int
    replay_case: ReplayCase
    outcome_snapshots: tuple[QuoteSnapshot, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "outcome_snapshots", tuple(self.outcome_snapshots))
        if self.sequence < 1:
            raise ValueError("record sequence must be >= 1")
        if self.previous_record_sha256 is not None:
            _sha256_text(self.previous_record_sha256, "previous_record_sha256")
        if self.phase not in _ALLOWED_PHASES:
            raise ValueError("record phase is invalid")
        if self.captured_at_ms < self.replay_case.evaluation_time_ms:
            raise ValueError("record capture cannot precede decision time")

        if self.phase == "DECISION":
            if self.replay_case.attempt != 1 or self.replay_case.outcome.terminal:
                raise ValueError("decision record must contain nonterminal attempt 1")
            if self.outcome_snapshots:
                raise ValueError("decision record cannot contain outcome snapshots")
        else:
            if self.replay_case.attempt < 2 or not self.replay_case.outcome.terminal:
                raise ValueError("outcome record must contain a terminal retry")
            if self.replay_case.outcome.realized_net_edge_bps is not None:
                if not self.outcome_snapshots:
                    raise ValueError("realized outcome requires public outcome snapshots")
                recomputed = realized_future_edge_bps(
                    self.replay_case,
                    self.outcome_snapshots,
                    observed_at_ms=self.replay_case.outcome.observed_at_ms,
                )
                if not math.isclose(
                    recomputed,
                    self.replay_case.outcome.realized_net_edge_bps,
                    rel_tol=0.0,
                    abs_tol=1e-12,
                ):
                    raise ValueError("record realized edge does not match outcome snapshots")

    def canonical_payload(self) -> dict[str, Any]:
        return {
            "schema": _RECORD_SCHEMA,
            "sequence": self.sequence,
            "previous_record_sha256": self.previous_record_sha256,
            "phase": self.phase,
            "captured_at_ms": self.captured_at_ms,
            "public_market_data_only": True,
            "replay_case": self.replay_case.canonical_payload(),
            "outcome_snapshots": [
                asdict(snapshot) for snapshot in self.outcome_snapshots
            ],
        }

    @property
    def sha256(self) -> str:
        return _sha256(self.canonical_payload())

    @classmethod
    def from_payload(cls, payload: Mapping[str, Any]) -> "RealMarketReplayRecord":
        if payload.get("schema") != _RECORD_SCHEMA:
            raise ValueError("unsupported real-market replay record schema")
        if payload.get("public_market_data_only") is not True:
            raise ValueError("real-market corpus only accepts public market data")
        try:
            record = cls(
                sequence=payload["sequence"],
                previous_record_sha256=payload["previous_record_sha256"],
                phase=payload["phase"],
                captured_at_ms=payload["captured_at_ms"],
                replay_case=ReplayCase.from_payload(payload["replay_case"]),
                outcome_snapshots=tuple(
                    QuoteSnapshot(**raw) for raw in payload["outcome_snapshots"]
                ),
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError("invalid real-market replay record payload") from exc
        if record.canonical_payload() != dict(payload):
            raise ValueError("real-market replay record payload is not canonical")
        return record


@dataclass(frozen=True, slots=True)
class RealMarketReplayCorpus:
    records: tuple[RealMarketReplayRecord, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "records", tuple(self.records))
        previous_sha: str | None = None
        cases: list[ReplayCase] = []
        for expected_sequence, record in enumerate(self.records, start=1):
            if record.sequence != expected_sequence:
                raise ValueError("corpus record sequence is not contiguous")
            if record.previous_record_sha256 != previous_sha:
                raise ValueError("corpus record hash chain is broken")
            previous_sha = record.sha256
            cases.append(record.replay_case)
        if cases:
            ReplayBundle(cases=tuple(cases))

    @property
    def sha256(self) -> str:
        return _sha256(self.canonical_payload())

    def canonical_payload(self) -> dict[str, Any]:
        return {
            "schema": _CORPUS_SCHEMA,
            "records": [record.canonical_payload() for record in self.records],
        }

    def to_envelope(self) -> dict[str, Any]:
        return {"payload": self.canonical_payload(), "sha256": self.sha256}

    @classmethod
    def from_envelope(cls, envelope: Mapping[str, Any]) -> "RealMarketReplayCorpus":
        try:
            payload = envelope["payload"]
            supplied_sha = envelope["sha256"]
        except KeyError as exc:
            raise ValueError("real-market corpus envelope is incomplete") from exc
        if not isinstance(payload, dict) or not isinstance(supplied_sha, str):
            raise ValueError("real-market corpus envelope has invalid types")
        if payload.get("schema") != _CORPUS_SCHEMA:
            raise ValueError("unsupported real-market replay corpus schema")
        digest = _sha256(payload)
        if not hmac.compare_digest(digest, supplied_sha):
            raise ValueError("real-market corpus SHA-256 does not match payload")
        try:
            corpus = cls(
                records=tuple(
                    RealMarketReplayRecord.from_payload(raw)
                    for raw in payload["records"]
                )
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError("invalid real-market replay corpus payload") from exc
        if corpus.canonical_payload() != payload:
            raise ValueError("real-market replay corpus payload is not canonical")
        if not hmac.compare_digest(corpus.sha256, supplied_sha):
            raise ValueError("reconstructed real-market corpus digest mismatch")
        return corpus

    def append_decisions(
        self,
        cases: Sequence[ReplayCase],
        *,
        captured_at_ms: int,
    ) -> "RealMarketReplayCorpus":
        records = list(self.records)
        previous_sha = records[-1].sha256 if records else None
        existing_operations = {
            record.replay_case.logical_operation_id for record in records
        }
        for case in cases:
            if case.logical_operation_id in existing_operations:
                raise ValueError("decision logical operation already exists in corpus")
            record = RealMarketReplayRecord(
                sequence=len(records) + 1,
                previous_record_sha256=previous_sha,
                phase="DECISION",
                captured_at_ms=captured_at_ms,
                replay_case=case,
            )
            records.append(record)
            previous_sha = record.sha256
            existing_operations.add(case.logical_operation_id)
        return RealMarketReplayCorpus(records=tuple(records))

    def pending_cases(self) -> tuple[ReplayCase, ...]:
        latest: dict[str, ReplayCase] = {}
        for record in self.records:
            case = record.replay_case
            current = latest.get(case.logical_operation_id)
            if current is None or case.attempt > current.attempt:
                latest[case.logical_operation_id] = case
        return tuple(
            case
            for case in sorted(
                latest.values(),
                key=lambda item: (item.detected_at_ms, item.logical_operation_id),
            )
            if not case.outcome.terminal
        )

    def append_outcome(
        self,
        case: ReplayCase,
        outcome_snapshots: Sequence[QuoteSnapshot],
        *,
        captured_at_ms: int,
    ) -> "RealMarketReplayCorpus":
        pending = {
            item.logical_operation_id: item for item in self.pending_cases()
        }
        try:
            expected = pending[case.logical_operation_id]
        except KeyError as exc:
            raise ValueError("outcome does not correspond to a pending operation") from exc
        if (
            case.attempt != expected.attempt + 1
            or case.decision_fingerprint != expected.decision_fingerprint
        ):
            raise ValueError("outcome retry does not preserve decision identity")

        records = list(self.records)
        previous_sha = records[-1].sha256 if records else None
        record = RealMarketReplayRecord(
            sequence=len(records) + 1,
            previous_record_sha256=previous_sha,
            phase="OUTCOME",
            captured_at_ms=captured_at_ms,
            replay_case=case,
            outcome_snapshots=tuple(outcome_snapshots),
        )
        records.append(record)
        return RealMarketReplayCorpus(records=tuple(records))

    def to_replay_bundle(self) -> ReplayBundle:
        if not self.records:
            raise ValueError("cannot export an empty real-market corpus")
        return ReplayBundle(
            cases=tuple(record.replay_case for record in self.records)
        )


def load_corpus(path: str | Path) -> RealMarketReplayCorpus:
    source = Path(path)
    if not source.exists():
        return RealMarketReplayCorpus()
    envelope = json.loads(source.read_text(encoding="utf-8"))
    return RealMarketReplayCorpus.from_envelope(envelope)


def save_corpus(path: str | Path, corpus: RealMarketReplayCorpus) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(destination.name + ".tmp")
    temporary.write_text(
        json.dumps(corpus.to_envelope(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(destination)


def export_replay_bundle(path: str | Path, corpus: RealMarketReplayCorpus) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(corpus.to_replay_bundle().to_envelope(), indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )
