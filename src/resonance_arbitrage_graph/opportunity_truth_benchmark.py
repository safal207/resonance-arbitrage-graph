from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from enum import Enum
import hashlib
import hmac
import json
import math
from statistics import mean
from types import MappingProxyType
from typing import Any

from .corpus_quality import (
    CorpusQualityPolicy,
    CorpusQualityReport,
    build_corpus_quality_report,
)
from .model import Verdict
from .observation import OutcomeClass
from .real_market_corpus import RealMarketReplayCorpus
from .replay import ReplayBundle, ReplayResult, benchmark_bundle


_REPORT_SCHEMA = "resonance.arbitrage.opportunity-truth-benchmark/v0.1"
_CLAIM_POLICY_SCHEMA = "resonance.arbitrage.benchmark-claim-policy/v0.1"


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


def _sha256_text(value: Any, name: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise ValueError(f"{name} must be a lowercase SHA-256 digest")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{name} must be hexadecimal") from exc
    if value.lower() != value:
        raise ValueError(f"{name} must be lowercase")
    return value


def _finite_optional(value: float | None, name: str) -> None:
    if value is not None and not math.isfinite(value):
        raise ValueError(f"{name} must be finite when supplied")


def _close(left: float, right: float) -> bool:
    return math.isclose(left, right, rel_tol=0.0, abs_tol=1e-12)


class BenchmarkSourceKind(str, Enum):
    REAL_MARKET_CORPUS = "REAL_MARKET_CORPUS"
    REPLAY_BUNDLE = "REPLAY_BUNDLE"


class BenchmarkClaimStatus(str, Enum):
    NOT_READY = "NOT_READY"
    INTERNAL_EVIDENCE_READY = "INTERNAL_EVIDENCE_READY"
    UNASSESSED_REPLAY_SOURCE = "UNASSESSED_REPLAY_SOURCE"


@dataclass(frozen=True, slots=True)
class BenchmarkClaimPolicy:
    min_terminal_operations: int = 100
    min_truth_events: int = 30
    require_corpus_quality: bool = True

    def __post_init__(self) -> None:
        for name in ("min_terminal_operations", "min_truth_events"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value < 1:
                raise ValueError(f"{name} must be an integer >= 1")
        if not isinstance(self.require_corpus_quality, bool):
            raise ValueError("require_corpus_quality must be boolean")

    def to_payload(self) -> dict[str, Any]:
        return {
            "schema": _CLAIM_POLICY_SCHEMA,
            "min_terminal_operations": self.min_terminal_operations,
            "min_truth_events": self.min_truth_events,
            "require_corpus_quality": self.require_corpus_quality,
            "interpretation": "INTERNAL_PRODUCT_EVIDENCE_READINESS_ONLY",
        }

    @property
    def sha256(self) -> str:
        return _sha256(self.to_payload())

    @classmethod
    def from_payload(cls, payload: Mapping[str, Any]) -> "BenchmarkClaimPolicy":
        if payload.get("schema") != _CLAIM_POLICY_SCHEMA:
            raise ValueError("unsupported benchmark claim policy schema")
        if payload.get("interpretation") != "INTERNAL_PRODUCT_EVIDENCE_READINESS_ONLY":
            raise ValueError("invalid benchmark claim policy interpretation")
        try:
            policy = cls(
                min_terminal_operations=payload["min_terminal_operations"],
                min_truth_events=payload["min_truth_events"],
                require_corpus_quality=payload["require_corpus_quality"],
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError("invalid benchmark claim policy payload") from exc
        if policy.to_payload() != dict(payload):
            raise ValueError("benchmark claim policy payload is not canonical")
        return policy


@dataclass(frozen=True, slots=True)
class DecisionFunnel:
    candidate_opportunities: int
    execute_sim: int
    observe: int
    reject: int
    true_positive: int
    false_positive: int
    expired: int
    rejected_outcomes: int
    indeterminate: int
    pending_execute_sim: int

    def __post_init__(self) -> None:
        for name in (
            "candidate_opportunities",
            "execute_sim",
            "observe",
            "reject",
            "true_positive",
            "false_positive",
            "expired",
            "rejected_outcomes",
            "indeterminate",
            "pending_execute_sim",
        ):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise ValueError(f"{name} must be a non-negative integer")
        if self.execute_sim + self.observe + self.reject != self.candidate_opportunities:
            raise ValueError("decision funnel verdict counts do not equal candidates")
        if (
            self.true_positive
            + self.false_positive
            + self.expired
            + self.rejected_outcomes
            + self.indeterminate
            != self.candidate_opportunities
        ):
            raise ValueError("decision funnel outcome counts do not equal candidates")
        if self.rejected_outcomes != self.reject:
            raise ValueError("REJECT decisions must map to REJECTED outcomes")
        if self.indeterminate != self.observe + self.pending_execute_sim:
            raise ValueError("indeterminate population must equal OBSERVE plus pending EXECUTE_SIM")
        if (
            self.true_positive
            + self.false_positive
            + self.expired
            + self.pending_execute_sim
            != self.execute_sim
        ):
            raise ValueError("EXECUTE_SIM outcome partition is inconsistent")

    @property
    def truth_events(self) -> int:
        return self.true_positive + self.false_positive

    def to_payload(self) -> dict[str, int]:
        return {
            "candidate_opportunities": self.candidate_opportunities,
            "execute_sim": self.execute_sim,
            "observe": self.observe,
            "reject": self.reject,
            "true_positive": self.true_positive,
            "false_positive": self.false_positive,
            "expired": self.expired,
            "rejected_outcomes": self.rejected_outcomes,
            "indeterminate": self.indeterminate,
            "pending_execute_sim": self.pending_execute_sim,
            "truth_events": self.truth_events,
        }

    @classmethod
    def from_payload(cls, payload: Mapping[str, Any]) -> "DecisionFunnel":
        expected = {
            "candidate_opportunities",
            "execute_sim",
            "observe",
            "reject",
            "true_positive",
            "false_positive",
            "expired",
            "rejected_outcomes",
            "indeterminate",
            "pending_execute_sim",
            "truth_events",
        }
        if set(payload) != expected:
            raise ValueError("decision funnel payload is not canonical")
        funnel = cls(
            candidate_opportunities=payload["candidate_opportunities"],
            execute_sim=payload["execute_sim"],
            observe=payload["observe"],
            reject=payload["reject"],
            true_positive=payload["true_positive"],
            false_positive=payload["false_positive"],
            expired=payload["expired"],
            rejected_outcomes=payload["rejected_outcomes"],
            indeterminate=payload["indeterminate"],
            pending_execute_sim=payload["pending_execute_sim"],
        )
        if payload["truth_events"] != funnel.truth_events:
            raise ValueError("decision funnel truth_events is inconsistent")
        return funnel


@dataclass(frozen=True, slots=True)
class BenchmarkSlice:
    key: str
    funnel: DecisionFunnel
    opportunity_truth_rate: float | None
    false_opportunity_rate: float | None
    route_survival_rate: float | None
    truth_coverage: float | None
    mean_expected_edge_bps: float | None
    mean_observed_edge_bps: float | None
    mean_edge_decay_bps: float | None
    mean_prediction_error_bps: float | None

    def __post_init__(self) -> None:
        if not isinstance(self.key, str) or not self.key:
            raise ValueError("benchmark slice key must be non-empty")
        if not isinstance(self.funnel, DecisionFunnel):
            raise ValueError("benchmark slice funnel has invalid type")
        for name in (
            "opportunity_truth_rate",
            "false_opportunity_rate",
            "route_survival_rate",
            "truth_coverage",
            "mean_expected_edge_bps",
            "mean_observed_edge_bps",
            "mean_edge_decay_bps",
            "mean_prediction_error_bps",
        ):
            _finite_optional(getattr(self, name), name)

        truth = self.funnel.truth_events
        survival_population = truth + self.funnel.expired
        expected_otr = self.funnel.true_positive / truth if truth else None
        expected_for = self.funnel.false_positive / truth if truth else None
        expected_survival = truth / survival_population if survival_population else None
        expected_coverage = truth / self.funnel.execute_sim if self.funnel.execute_sim else None
        for name, supplied, expected in (
            ("opportunity_truth_rate", self.opportunity_truth_rate, expected_otr),
            ("false_opportunity_rate", self.false_opportunity_rate, expected_for),
            ("route_survival_rate", self.route_survival_rate, expected_survival),
            ("truth_coverage", self.truth_coverage, expected_coverage),
        ):
            if supplied is None or expected is None:
                if supplied is not expected:
                    raise ValueError(f"{name} is inconsistent with funnel")
            elif not _close(supplied, expected):
                raise ValueError(f"{name} is inconsistent with funnel")

        edge_values = (
            self.mean_expected_edge_bps,
            self.mean_observed_edge_bps,
            self.mean_edge_decay_bps,
            self.mean_prediction_error_bps,
        )
        if truth == 0:
            if any(value is not None for value in edge_values):
                raise ValueError("edge means require determinate truth events")
        else:
            if any(value is None for value in edge_values):
                raise ValueError("determinate truth events require edge means")
            assert self.mean_expected_edge_bps is not None
            assert self.mean_observed_edge_bps is not None
            assert self.mean_edge_decay_bps is not None
            assert self.mean_prediction_error_bps is not None
            if not _close(
                self.mean_edge_decay_bps,
                self.mean_expected_edge_bps - self.mean_observed_edge_bps,
            ):
                raise ValueError("mean edge decay is inconsistent")
            if not _close(
                self.mean_prediction_error_bps,
                self.mean_observed_edge_bps - self.mean_expected_edge_bps,
            ):
                raise ValueError("mean prediction error is inconsistent")

    def to_payload(self) -> dict[str, Any]:
        return {
            "key": self.key,
            "funnel": self.funnel.to_payload(),
            "opportunity_truth_rate": self.opportunity_truth_rate,
            "false_opportunity_rate": self.false_opportunity_rate,
            "route_survival_rate": self.route_survival_rate,
            "truth_coverage": self.truth_coverage,
            "mean_expected_edge_bps": self.mean_expected_edge_bps,
            "mean_observed_edge_bps": self.mean_observed_edge_bps,
            "mean_edge_decay_bps": self.mean_edge_decay_bps,
            "mean_prediction_error_bps": self.mean_prediction_error_bps,
        }

    @classmethod
    def from_payload(cls, payload: Mapping[str, Any]) -> "BenchmarkSlice":
        expected = {
            "key",
            "funnel",
            "opportunity_truth_rate",
            "false_opportunity_rate",
            "route_survival_rate",
            "truth_coverage",
            "mean_expected_edge_bps",
            "mean_observed_edge_bps",
            "mean_edge_decay_bps",
            "mean_prediction_error_bps",
        }
        if set(payload) != expected or not isinstance(payload.get("funnel"), Mapping):
            raise ValueError("benchmark slice payload is not canonical")
        return cls(
            key=payload["key"],
            funnel=DecisionFunnel.from_payload(payload["funnel"]),
            opportunity_truth_rate=payload["opportunity_truth_rate"],
            false_opportunity_rate=payload["false_opportunity_rate"],
            route_survival_rate=payload["route_survival_rate"],
            truth_coverage=payload["truth_coverage"],
            mean_expected_edge_bps=payload["mean_expected_edge_bps"],
            mean_observed_edge_bps=payload["mean_observed_edge_bps"],
            mean_edge_decay_bps=payload["mean_edge_decay_bps"],
            mean_prediction_error_bps=payload["mean_prediction_error_bps"],
        )


@dataclass(frozen=True, slots=True)
class PaperPnlSlice:
    start_state: str
    truth_events: int
    aggregate_expected_pnl_units: float
    aggregate_observed_pnl_units: float
    aggregate_pnl_delta_units: float
    mean_expected_pnl_units: float
    mean_observed_pnl_units: float

    def __post_init__(self) -> None:
        if not isinstance(self.start_state, str) or not self.start_state:
            raise ValueError("paper PnL start_state must be non-empty")
        if isinstance(self.truth_events, bool) or not isinstance(self.truth_events, int) or self.truth_events < 1:
            raise ValueError("paper PnL truth_events must be an integer >= 1")
        for name in (
            "aggregate_expected_pnl_units",
            "aggregate_observed_pnl_units",
            "aggregate_pnl_delta_units",
            "mean_expected_pnl_units",
            "mean_observed_pnl_units",
        ):
            value = getattr(self, name)
            if not math.isfinite(value):
                raise ValueError(f"{name} must be finite")
        if not _close(
            self.aggregate_pnl_delta_units,
            self.aggregate_observed_pnl_units - self.aggregate_expected_pnl_units,
        ):
            raise ValueError("aggregate paper PnL delta is inconsistent")
        if not _close(
            self.mean_expected_pnl_units,
            self.aggregate_expected_pnl_units / self.truth_events,
        ):
            raise ValueError("mean expected paper PnL is inconsistent")
        if not _close(
            self.mean_observed_pnl_units,
            self.aggregate_observed_pnl_units / self.truth_events,
        ):
            raise ValueError("mean observed paper PnL is inconsistent")

    def to_payload(self) -> dict[str, Any]:
        return {
            "start_state": self.start_state,
            "truth_events": self.truth_events,
            "aggregate_expected_pnl_units": self.aggregate_expected_pnl_units,
            "aggregate_observed_pnl_units": self.aggregate_observed_pnl_units,
            "aggregate_pnl_delta_units": self.aggregate_pnl_delta_units,
            "mean_expected_pnl_units": self.mean_expected_pnl_units,
            "mean_observed_pnl_units": self.mean_observed_pnl_units,
        }

    @classmethod
    def from_payload(cls, payload: Mapping[str, Any]) -> "PaperPnlSlice":
        expected = {
            "start_state",
            "truth_events",
            "aggregate_expected_pnl_units",
            "aggregate_observed_pnl_units",
            "aggregate_pnl_delta_units",
            "mean_expected_pnl_units",
            "mean_observed_pnl_units",
        }
        if set(payload) != expected:
            raise ValueError("paper PnL slice payload is not canonical")
        return cls(**dict(payload))


def _build_funnel(results: Sequence[ReplayResult]) -> DecisionFunnel:
    verdicts = Counter(result.expected_verdict for result in results)
    outcomes = Counter(result.outcome_class for result in results)
    pending_execute = sum(
        result.expected_verdict is Verdict.EXECUTE_SIM
        and result.outcome_class is OutcomeClass.INDETERMINATE
        for result in results
    )
    return DecisionFunnel(
        candidate_opportunities=len(results),
        execute_sim=verdicts[Verdict.EXECUTE_SIM],
        observe=verdicts[Verdict.OBSERVE],
        reject=verdicts[Verdict.REJECT],
        true_positive=outcomes[OutcomeClass.TRUE_POSITIVE],
        false_positive=outcomes[OutcomeClass.FALSE_POSITIVE],
        expired=outcomes[OutcomeClass.EXPIRED],
        rejected_outcomes=outcomes[OutcomeClass.REJECTED],
        indeterminate=outcomes[OutcomeClass.INDETERMINATE],
        pending_execute_sim=pending_execute,
    )


def _build_slice(key: str, results: Sequence[ReplayResult]) -> BenchmarkSlice:
    rows = tuple(results)
    funnel = _build_funnel(rows)
    truth_rows = tuple(
        result
        for result in rows
        if result.outcome_class in {
            OutcomeClass.TRUE_POSITIVE,
            OutcomeClass.FALSE_POSITIVE,
        }
    )
    if truth_rows:
        expected = mean(result.expected_edge_bps for result in truth_rows)
        observed = mean(
            result.observed_edge_bps
            for result in truth_rows
            if result.observed_edge_bps is not None
        )
        decay = expected - observed
        error = observed - expected
    else:
        expected = observed = decay = error = None
    truth = funnel.truth_events
    survival_population = truth + funnel.expired
    return BenchmarkSlice(
        key=key,
        funnel=funnel,
        opportunity_truth_rate=(funnel.true_positive / truth if truth else None),
        false_opportunity_rate=(funnel.false_positive / truth if truth else None),
        route_survival_rate=(truth / survival_population if survival_population else None),
        truth_coverage=(truth / funnel.execute_sim if funnel.execute_sim else None),
        mean_expected_edge_bps=expected,
        mean_observed_edge_bps=observed,
        mean_edge_decay_bps=decay,
        mean_prediction_error_bps=error,
    )


def _build_pnl_slices(
    bundle: ReplayBundle,
    results: Sequence[ReplayResult],
) -> tuple[PaperPnlSlice, ...]:
    cases = {
        case.logical_operation_id: case for case in bundle.collapsed_cases()
    }
    grouped: dict[str, list[tuple[float, float]]] = defaultdict(list)
    for result in results:
        if result.outcome_class not in {
            OutcomeClass.TRUE_POSITIVE,
            OutcomeClass.FALSE_POSITIVE,
        }:
            continue
        if result.observed_edge_bps is None:
            raise ValueError("truth event is missing observed edge")
        case = cases[result.logical_operation_id]
        route = case.build_route()
        start = route[0].src
        start_state = f"{start.venue}:{start.asset}"
        expected_pnl = case.start_amount * result.expected_edge_bps / 10_000.0
        observed_pnl = case.start_amount * result.observed_edge_bps / 10_000.0
        grouped[start_state].append((expected_pnl, observed_pnl))
    slices: list[PaperPnlSlice] = []
    for start_state in sorted(grouped):
        rows = grouped[start_state]
        aggregate_expected = sum(item[0] for item in rows)
        aggregate_observed = sum(item[1] for item in rows)
        slices.append(
            PaperPnlSlice(
                start_state=start_state,
                truth_events=len(rows),
                aggregate_expected_pnl_units=aggregate_expected,
                aggregate_observed_pnl_units=aggregate_observed,
                aggregate_pnl_delta_units=aggregate_observed - aggregate_expected,
                mean_expected_pnl_units=aggregate_expected / len(rows),
                mean_observed_pnl_units=aggregate_observed / len(rows),
            )
        )
    return tuple(slices)


def _claim_decision(
    *,
    source_kind: BenchmarkSourceKind,
    overall: BenchmarkSlice,
    claim_policy: BenchmarkClaimPolicy,
    quality_report: CorpusQualityReport | None,
) -> tuple[BenchmarkClaimStatus, tuple[str, ...]]:
    if source_kind is BenchmarkSourceKind.REPLAY_BUNDLE:
        return (
            BenchmarkClaimStatus.UNASSESSED_REPLAY_SOURCE,
            ("claim readiness requires append-only real-market corpus provenance",),
        )
    if quality_report is None:
        raise ValueError("real-market claim decision requires corpus quality report")
    failures: list[str] = []
    if quality_report.terminal_operation_count < claim_policy.min_terminal_operations:
        failures.append("terminal_operations")
    if overall.funnel.truth_events < claim_policy.min_truth_events:
        failures.append("truth_events")
    if claim_policy.require_corpus_quality and not quality_report.quality_ready:
        failures.extend(
            f"corpus_quality:{dimension}"
            for dimension in quality_report.failed_dimensions
        )
    if failures:
        return BenchmarkClaimStatus.NOT_READY, tuple(failures)
    return BenchmarkClaimStatus.INTERNAL_EVIDENCE_READY, ()


@dataclass(frozen=True, slots=True)
class OpportunityTruthBenchmarkReport:
    source_kind: BenchmarkSourceKind
    source_sha256: str
    replay_bundle_sha256: str
    calibration_report_sha256: str
    operation_ids: tuple[str, ...]
    claim_policy: BenchmarkClaimPolicy
    claim_status: BenchmarkClaimStatus
    claim_reasons: tuple[str, ...]
    corpus_quality_payload: Mapping[str, Any] | None
    corpus_quality_sha256: str | None
    overall: BenchmarkSlice
    by_regime: tuple[BenchmarkSlice, ...]
    by_route: tuple[BenchmarkSlice, ...]
    reason_counts: tuple[tuple[str, int], ...]
    paper_pnl_by_start_state: tuple[PaperPnlSlice, ...]
    paper_only: bool = True
    no_live_profitability_claim: bool = True

    def __post_init__(self) -> None:
        if not isinstance(self.source_kind, BenchmarkSourceKind):
            raise ValueError("benchmark source kind has invalid type")
        _sha256_text(self.source_sha256, "source_sha256")
        _sha256_text(self.replay_bundle_sha256, "replay_bundle_sha256")
        _sha256_text(self.calibration_report_sha256, "calibration_report_sha256")
        object.__setattr__(self, "operation_ids", tuple(self.operation_ids))
        if tuple(sorted(self.operation_ids)) != self.operation_ids or len(set(self.operation_ids)) != len(self.operation_ids):
            raise ValueError("benchmark operation_ids must be sorted and unique")
        if len(self.operation_ids) != self.overall.funnel.candidate_opportunities:
            raise ValueError("benchmark operation membership does not match overall funnel")
        if not isinstance(self.claim_policy, BenchmarkClaimPolicy):
            raise ValueError("benchmark claim policy has invalid type")
        if not isinstance(self.claim_status, BenchmarkClaimStatus):
            raise ValueError("benchmark claim status has invalid type")
        object.__setattr__(self, "claim_reasons", tuple(self.claim_reasons))
        if self.claim_status is BenchmarkClaimStatus.INTERNAL_EVIDENCE_READY:
            if self.claim_reasons:
                raise ValueError("ready benchmark cannot contain claim failure reasons")
        elif not self.claim_reasons:
            raise ValueError("non-ready benchmark must explain claim status")

        if self.corpus_quality_payload is None:
            if self.corpus_quality_sha256 is not None:
                raise ValueError("quality SHA cannot exist without quality payload")
            if self.source_kind is BenchmarkSourceKind.REAL_MARKET_CORPUS:
                raise ValueError("real-market benchmark requires quality evidence")
        else:
            payload = dict(self.corpus_quality_payload)
            object.__setattr__(self, "corpus_quality_payload", MappingProxyType(payload))
            if self.corpus_quality_sha256 is None:
                raise ValueError("quality payload requires quality SHA")
            _sha256_text(self.corpus_quality_sha256, "corpus_quality_sha256")
            if not hmac.compare_digest(_sha256(payload), self.corpus_quality_sha256):
                raise ValueError("corpus quality SHA does not match payload")
            if payload.get("corpus_sha256") != self.source_sha256:
                raise ValueError("corpus quality report binds a different source")

        object.__setattr__(self, "by_regime", tuple(self.by_regime))
        object.__setattr__(self, "by_route", tuple(self.by_route))
        for name in ("by_regime", "by_route"):
            values = getattr(self, name)
            keys = tuple(item.key for item in values)
            if keys != tuple(sorted(keys)) or len(set(keys)) != len(keys):
                raise ValueError(f"{name} must be uniquely sorted")
        object.__setattr__(self, "reason_counts", tuple(self.reason_counts))
        reason_keys = tuple(key for key, _ in self.reason_counts)
        if reason_keys != tuple(sorted(reason_keys)) or len(set(reason_keys)) != len(reason_keys):
            raise ValueError("reason_counts must be uniquely sorted")
        if any(not key or isinstance(count, bool) or not isinstance(count, int) or count < 1 for key, count in self.reason_counts):
            raise ValueError("reason_counts entries are invalid")
        object.__setattr__(
            self,
            "paper_pnl_by_start_state",
            tuple(self.paper_pnl_by_start_state),
        )
        states = tuple(item.start_state for item in self.paper_pnl_by_start_state)
        if states != tuple(sorted(states)) or len(set(states)) != len(states):
            raise ValueError("paper PnL slices must be uniquely sorted")
        if self.paper_only is not True or self.no_live_profitability_claim is not True:
            raise ValueError("benchmark must remain paper-only without live profitability claim")

        quality_report = None
        if self.corpus_quality_payload is not None:
            quality_report = _quality_from_payload(self.corpus_quality_payload)
        expected_status, expected_reasons = _claim_decision(
            source_kind=self.source_kind,
            overall=self.overall,
            claim_policy=self.claim_policy,
            quality_report=quality_report,
        )
        if self.claim_status is not expected_status or self.claim_reasons != expected_reasons:
            raise ValueError("benchmark claim status does not match bound evidence")

    def canonical_payload(self) -> dict[str, Any]:
        return {
            "schema": _REPORT_SCHEMA,
            "source_kind": self.source_kind.value,
            "source_sha256": self.source_sha256,
            "replay_bundle_sha256": self.replay_bundle_sha256,
            "calibration_report_sha256": self.calibration_report_sha256,
            "operation_ids": list(self.operation_ids),
            "claim_policy_sha256": self.claim_policy.sha256,
            "claim_policy": self.claim_policy.to_payload(),
            "claim_status": self.claim_status.value,
            "claim_reasons": list(self.claim_reasons),
            "corpus_quality_sha256": self.corpus_quality_sha256,
            "corpus_quality": (
                dict(self.corpus_quality_payload)
                if self.corpus_quality_payload is not None
                else None
            ),
            "overall": self.overall.to_payload(),
            "by_regime": [item.to_payload() for item in self.by_regime],
            "by_route": [item.to_payload() for item in self.by_route],
            "reason_counts": [
                {"reason": reason, "operations": count}
                for reason, count in self.reason_counts
            ],
            "paper_pnl_by_start_state": [
                item.to_payload() for item in self.paper_pnl_by_start_state
            ],
            "paper_only": self.paper_only,
            "no_live_profitability_claim": self.no_live_profitability_claim,
            "rejected_not_counted_as_false_positive": True,
            "indeterminate_not_counted_as_truth_event": True,
            "paper_pnl_units_are_not_cross_asset_aggregated": True,
        }

    @property
    def sha256(self) -> str:
        return _sha256(self.canonical_payload())

    def to_envelope(self) -> dict[str, Any]:
        return {"payload": self.canonical_payload(), "sha256": self.sha256}

    @classmethod
    def from_payload(
        cls, payload: Mapping[str, Any]
    ) -> "OpportunityTruthBenchmarkReport":
        return _report_from_payload(payload)


def _quality_from_payload(payload: Mapping[str, Any]) -> CorpusQualityReport:
    policy_payload = payload.get("policy_payload")
    if not isinstance(policy_payload, Mapping):
        raise ValueError("corpus quality payload lacks policy")
    policy = CorpusQualityPolicy.from_payload(policy_payload)
    try:
        decision_batch_counts = tuple(
            (row["evaluation_time_ms"], row["terminal_operations"])
            for row in payload["decision_batch_counts"]
        )
        route_topology_counts = tuple(
            (row["route_topology_id"], row["terminal_operations"])
            for row in payload["route_topology_counts"]
        )
        regime_counts = tuple(
            (row["regime"], row["terminal_operations"])
            for row in payload["regime_counts"]
        )
        report = CorpusQualityReport(
            corpus_sha256=payload["corpus_sha256"],
            policy_sha256=payload["policy_sha256"],
            policy_payload=policy.to_payload(),
            terminal_operation_count=payload["terminal_operation_count"],
            decision_batch_counts=decision_batch_counts,
            effective_decision_batches=payload["effective_decision_batches"],
            largest_decision_batch_share=payload["largest_decision_batch_share"],
            temporal_span_ms=payload["temporal_span_ms"],
            route_topology_counts=route_topology_counts,
            effective_routes=payload["effective_routes"],
            largest_route_share=payload["largest_route_share"],
            route_market_identities=tuple(payload["route_market_identities"]),
            regime_counts=regime_counts,
            failed_dimensions=tuple(payload["failed_dimensions"]),
            quality_ready=payload["quality_ready"],
            paper_only=payload["paper_only"],
            public_market_data_only=payload["public_market_data_only"],
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("invalid corpus quality payload in benchmark") from exc
    if report.to_payload() != dict(payload):
        raise ValueError("corpus quality payload in benchmark is not canonical")
    return report


def build_opportunity_truth_benchmark(
    source: RealMarketReplayCorpus | ReplayBundle,
    *,
    claim_policy: BenchmarkClaimPolicy | None = None,
    quality_policy: CorpusQualityPolicy | None = None,
) -> OpportunityTruthBenchmarkReport:
    active_claim_policy = claim_policy or BenchmarkClaimPolicy()
    if isinstance(source, RealMarketReplayCorpus):
        source_kind = BenchmarkSourceKind.REAL_MARKET_CORPUS
        source_sha = source.sha256
        bundle = source.to_replay_bundle()
        quality_report = build_corpus_quality_report(
            source,
            policy=quality_policy or CorpusQualityPolicy(),
        )
    elif isinstance(source, ReplayBundle):
        source_kind = BenchmarkSourceKind.REPLAY_BUNDLE
        source_sha = source.sha256
        bundle = source
        quality_report = None
    else:
        raise ValueError("benchmark source must be RealMarketReplayCorpus or ReplayBundle")

    calibration = benchmark_bundle(bundle)
    results = calibration.results
    regime_groups: dict[str, list[ReplayResult]] = defaultdict(list)
    route_groups: dict[str, list[ReplayResult]] = defaultdict(list)
    reasons: Counter[str] = Counter()
    for result in results:
        regime_groups[result.regime.value].append(result)
        route_groups[result.route_id].append(result)
        reasons.update(set(result.reasons))

    overall = _build_slice("ALL", results)
    status, status_reasons = _claim_decision(
        source_kind=source_kind,
        overall=overall,
        claim_policy=active_claim_policy,
        quality_report=quality_report,
    )
    return OpportunityTruthBenchmarkReport(
        source_kind=source_kind,
        source_sha256=source_sha,
        replay_bundle_sha256=bundle.sha256,
        calibration_report_sha256=calibration.sha256,
        operation_ids=tuple(sorted(result.logical_operation_id for result in results)),
        claim_policy=active_claim_policy,
        claim_status=status,
        claim_reasons=status_reasons,
        corpus_quality_payload=(
            quality_report.to_payload() if quality_report is not None else None
        ),
        corpus_quality_sha256=(
            quality_report.sha256 if quality_report is not None else None
        ),
        overall=overall,
        by_regime=tuple(
            _build_slice(key, regime_groups[key]) for key in sorted(regime_groups)
        ),
        by_route=tuple(
            _build_slice(key, route_groups[key]) for key in sorted(route_groups)
        ),
        reason_counts=tuple(sorted(reasons.items())),
        paper_pnl_by_start_state=_build_pnl_slices(bundle, results),
    )


def _report_from_payload(payload: Mapping[str, Any]) -> OpportunityTruthBenchmarkReport:
    claim_payload = payload.get("claim_policy")
    overall_payload = payload.get("overall")
    if not isinstance(claim_payload, Mapping) or not isinstance(overall_payload, Mapping):
        raise ValueError("benchmark report nested payload is invalid")
    policy = BenchmarkClaimPolicy.from_payload(claim_payload)
    if payload.get("claim_policy_sha256") != policy.sha256:
        raise ValueError("benchmark claim policy SHA does not match payload")
    by_regime = payload.get("by_regime")
    by_route = payload.get("by_route")
    reason_counts = payload.get("reason_counts")
    pnl = payload.get("paper_pnl_by_start_state")
    if not all(isinstance(value, list) for value in (by_regime, by_route, reason_counts, pnl)):
        raise ValueError("benchmark report collections are invalid")
    try:
        report = OpportunityTruthBenchmarkReport(
            source_kind=BenchmarkSourceKind(payload["source_kind"]),
            source_sha256=payload["source_sha256"],
            replay_bundle_sha256=payload["replay_bundle_sha256"],
            calibration_report_sha256=payload["calibration_report_sha256"],
            operation_ids=tuple(payload["operation_ids"]),
            claim_policy=policy,
            claim_status=BenchmarkClaimStatus(payload["claim_status"]),
            claim_reasons=tuple(payload["claim_reasons"]),
            corpus_quality_payload=payload["corpus_quality"],
            corpus_quality_sha256=payload["corpus_quality_sha256"],
            overall=BenchmarkSlice.from_payload(overall_payload),
            by_regime=tuple(BenchmarkSlice.from_payload(item) for item in by_regime),
            by_route=tuple(BenchmarkSlice.from_payload(item) for item in by_route),
            reason_counts=tuple(
                (item["reason"], item["operations"]) for item in reason_counts
            ),
            paper_pnl_by_start_state=tuple(
                PaperPnlSlice.from_payload(item) for item in pnl
            ),
            paper_only=payload["paper_only"],
            no_live_profitability_claim=payload["no_live_profitability_claim"],
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("invalid opportunity truth benchmark payload") from exc
    if report.canonical_payload() != dict(payload):
        raise ValueError("opportunity truth benchmark payload is not canonical")
    return report


def verify_opportunity_truth_benchmark_envelope(
    envelope: Mapping[str, Any],
) -> dict[str, Any]:
    if not isinstance(envelope, Mapping) or set(envelope) != {"payload", "sha256"}:
        raise ValueError("opportunity truth benchmark envelope is not canonical")
    payload = envelope["payload"]
    supplied_sha = _sha256_text(envelope["sha256"], "benchmark_sha256")
    expected_keys = {
        "schema",
        "source_kind",
        "source_sha256",
        "replay_bundle_sha256",
        "calibration_report_sha256",
        "operation_ids",
        "claim_policy_sha256",
        "claim_policy",
        "claim_status",
        "claim_reasons",
        "corpus_quality_sha256",
        "corpus_quality",
        "overall",
        "by_regime",
        "by_route",
        "reason_counts",
        "paper_pnl_by_start_state",
        "paper_only",
        "no_live_profitability_claim",
        "rejected_not_counted_as_false_positive",
        "indeterminate_not_counted_as_truth_event",
        "paper_pnl_units_are_not_cross_asset_aggregated",
    }
    if not isinstance(payload, dict) or set(payload) != expected_keys:
        raise ValueError("opportunity truth benchmark payload fields are not canonical")
    if payload.get("schema") != _REPORT_SCHEMA:
        raise ValueError("unsupported opportunity truth benchmark schema")
    for flag in (
        "rejected_not_counted_as_false_positive",
        "indeterminate_not_counted_as_truth_event",
        "paper_pnl_units_are_not_cross_asset_aggregated",
    ):
        if payload.get(flag) is not True:
            raise ValueError(f"benchmark invariant flag is invalid: {flag}")
    report = _report_from_payload(payload)
    if not hmac.compare_digest(report.sha256, supplied_sha):
        raise ValueError("opportunity truth benchmark SHA-256 does not match payload")
    return dict(payload)


def verify_opportunity_truth_benchmark_source_binding(
    report: OpportunityTruthBenchmarkReport | Mapping[str, Any],
    source: RealMarketReplayCorpus | ReplayBundle,
) -> bool:
    bound_report = (
        report
        if isinstance(report, OpportunityTruthBenchmarkReport)
        else _report_from_payload(
            verify_opportunity_truth_benchmark_envelope(report)
        )
    )
    quality_policy = None
    if bound_report.corpus_quality_payload is not None:
        quality_policy = CorpusQualityPolicy.from_payload(
            bound_report.corpus_quality_payload["policy_payload"]
        )
    rebuilt = build_opportunity_truth_benchmark(
        source,
        claim_policy=bound_report.claim_policy,
        quality_policy=quality_policy,
    )
    if rebuilt.canonical_payload() != bound_report.canonical_payload():
        raise ValueError("opportunity truth benchmark does not reproduce from source")
    return True


def _percent(value: float | None) -> str:
    return "n/a" if value is None else f"{value * 100:.2f}%"


def _number(value: float | None, suffix: str = "") -> str:
    return "n/a" if value is None else f"{value:.4f}{suffix}"


def render_opportunity_truth_benchmark_markdown(
    report: OpportunityTruthBenchmarkReport,
) -> str:
    if not isinstance(report, OpportunityTruthBenchmarkReport):
        raise ValueError("report must be OpportunityTruthBenchmarkReport")
    overall = report.overall
    funnel = overall.funnel
    lines = [
        "# RESONANCE Verify — Opportunity Truth Benchmark",
        "",
        f"- **Claim status:** `{report.claim_status.value}`",
        f"- **Source:** `{report.source_kind.value}`",
        f"- **Source SHA-256:** `{report.source_sha256}`",
        f"- **Benchmark SHA-256:** `{report.sha256}`",
        "",
    ]
    if report.claim_reasons:
        lines.append("**Readiness blockers:** " + ", ".join(f"`{item}`" for item in report.claim_reasons))
        lines.append("")
    lines.extend(
        [
            "## Decision funnel",
            "",
            "| Stage | Operations |",
            "|---|---:|",
            f"| Candidate opportunities | {funnel.candidate_opportunities} |",
            f"| EXECUTE_SIM | {funnel.execute_sim} |",
            f"| OBSERVE | {funnel.observe} |",
            f"| REJECT | {funnel.reject} |",
            f"| True positives | {funnel.true_positive} |",
            f"| False positives | {funnel.false_positive} |",
            f"| Expired | {funnel.expired} |",
            f"| Pending EXECUTE_SIM | {funnel.pending_execute_sim} |",
            "",
            "## Core metrics",
            "",
            "| Metric | Value |",
            "|---|---:|",
            f"| Opportunity Truth Rate | {_percent(overall.opportunity_truth_rate)} |",
            f"| False Opportunity Rate | {_percent(overall.false_opportunity_rate)} |",
            f"| Route Survival Rate | {_percent(overall.route_survival_rate)} |",
            f"| Truth coverage of EXECUTE_SIM | {_percent(overall.truth_coverage)} |",
            f"| Mean expected edge | {_number(overall.mean_expected_edge_bps, ' bps')} |",
            f"| Mean observed edge | {_number(overall.mean_observed_edge_bps, ' bps')} |",
            f"| Mean edge decay | {_number(overall.mean_edge_decay_bps, ' bps')} |",
            "",
        ]
    )
    if report.paper_pnl_by_start_state:
        lines.extend(
            [
                "## Paper PnL by exact starting state",
                "",
                "| Start state | Truth events | Expected units | Observed units | Delta units |",
                "|---|---:|---:|---:|---:|",
            ]
        )
        for item in report.paper_pnl_by_start_state:
            lines.append(
                f"| `{item.start_state}` | {item.truth_events} | "
                f"{item.aggregate_expected_pnl_units:.6f} | "
                f"{item.aggregate_observed_pnl_units:.6f} | "
                f"{item.aggregate_pnl_delta_units:.6f} |"
            )
        lines.append("")

    if report.by_regime:
        lines.extend(
            [
                "## By market regime",
                "",
                "| Regime | Operations | Truth events | OTR | Survival | Edge decay |",
                "|---|---:|---:|---:|---:|---:|",
            ]
        )
        for item in report.by_regime:
            lines.append(
                f"| `{item.key}` | {item.funnel.candidate_opportunities} | "
                f"{item.funnel.truth_events} | {_percent(item.opportunity_truth_rate)} | "
                f"{_percent(item.route_survival_rate)} | "
                f"{_number(item.mean_edge_decay_bps, ' bps')} |"
            )
        lines.append("")

    if report.by_route:
        lines.extend(
            [
                "## By route",
                "",
                "| Route | Operations | Truth events | OTR | Survival | Edge decay |",
                "|---|---:|---:|---:|---:|---:|",
            ]
        )
        for item in report.by_route:
            lines.append(
                f"| `{item.key[:16]}…` | {item.funnel.candidate_opportunities} | "
                f"{item.funnel.truth_events} | {_percent(item.opportunity_truth_rate)} | "
                f"{_percent(item.route_survival_rate)} | "
                f"{_number(item.mean_edge_decay_bps, ' bps')} |"
            )
        lines.append("")

    if report.reason_counts:
        lines.extend(
            [
                "## Decision reason distribution",
                "",
                "| Reason | Operations |",
                "|---|---:|",
            ]
        )
        for reason, count in sorted(
            report.reason_counts,
            key=lambda item: (-item[1], item[0]),
        ):
            lines.append(f"| {reason} | {count} |")
        lines.append("")

    lines.extend(
        [
            "## Interpretation boundary",
            "",
            "This report measures deterministic **paper** outcomes from bound market evidence. "
            "It is not a live-fill, live-PnL, or profitability claim. Rejected opportunities are "
            "not counted as false positives, indeterminate outcomes are excluded from OTR, and "
            "PnL units are never aggregated across different starting assets or venues.",
            "",
        ]
    )
    return "\n".join(lines)
