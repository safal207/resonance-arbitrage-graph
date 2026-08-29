from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
import hashlib
import hmac
import json
import math
from statistics import mean
from typing import Any

from .engine import evaluate_route
from .model import Verdict
from .observation import OutcomeClass
from .opportunity_truth_benchmark import OpportunityTruthEvidenceSource
from .real_market_corpus import RealMarketReplayCorpus
from .regime import MarketRegime
from .replay import ReplayBundle, ReplayCase, ReplayResult, replay_case


_SCHEMA = "resonance.verify.opportunity-funnel/v0.1"
_STRUCTURAL_REASONS = {
    "NOT_A_CYCLE",
    "ROUTE_LATENCY_EXCEEDED",
    "SUCCESS_PROBABILITY_TOO_LOW",
}


def _json(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def _digest(value: Any) -> str:
    return hashlib.sha256(_json(value).encode("utf-8")).hexdigest()


def _sha(value: Any, name: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise ValueError(f"{name} must be a lowercase SHA-256 digest")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{name} must be hexadecimal") from exc
    if value.lower() != value:
        raise ValueError(f"{name} must be lowercase")
    return value


def _count(value: Any, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{name} must be a non-negative integer")
    return value


def _finite(value: Any, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be numeric")
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{name} must be finite")
    return result


def _is_structural_reason(reason: str) -> bool:
    return (
        reason in _STRUCTURAL_REASONS
        or reason.startswith("STALE_QUOTE:")
        or reason.startswith("CAPACITY_EXCEEDED:")
    )


@dataclass(frozen=True, slots=True)
class FunnelDistribution:
    count: int
    minimum_bps: float | None
    mean_bps: float | None
    maximum_bps: float | None

    def __post_init__(self) -> None:
        _count(self.count, "distribution count")
        values = (self.minimum_bps, self.mean_bps, self.maximum_bps)
        if self.count == 0:
            if any(value is not None for value in values):
                raise ValueError("empty distribution cannot contain values")
            return
        if any(value is None for value in values):
            raise ValueError("non-empty distribution requires min/mean/max")
        minimum = _finite(self.minimum_bps, "minimum_bps")
        average = _finite(self.mean_bps, "mean_bps")
        maximum = _finite(self.maximum_bps, "maximum_bps")
        if minimum > average or average > maximum:
            raise ValueError("distribution values are not ordered")

    @classmethod
    def from_values(cls, values: Sequence[float]) -> "FunnelDistribution":
        rows = tuple(float(value) for value in values)
        for value in rows:
            _finite(value, "distribution value")
        if not rows:
            return cls(0, None, None, None)
        return cls(len(rows), min(rows), mean(rows), max(rows))

    def to_payload(self) -> dict[str, Any]:
        return {
            "count": self.count,
            "minimum_bps": self.minimum_bps,
            "mean_bps": self.mean_bps,
            "maximum_bps": self.maximum_bps,
        }


@dataclass(frozen=True, slots=True)
class OpportunityFunnelCounts:
    candidate_cycles: int
    complete_evidence: int
    structural_constraints_pass: int
    gross_positive: int
    net_positive: int
    execute_threshold_eligible: int
    final_execute_sim: int
    resolved_execute_outcomes: int
    truth_outcomes: int
    survived_required_edge: int

    def __post_init__(self) -> None:
        names = (
            "candidate_cycles",
            "complete_evidence",
            "structural_constraints_pass",
            "gross_positive",
            "net_positive",
            "execute_threshold_eligible",
            "final_execute_sim",
            "resolved_execute_outcomes",
            "truth_outcomes",
            "survived_required_edge",
        )
        values = tuple(_count(getattr(self, name), name) for name in names)
        for previous, current in zip(values, values[1:]):
            if current > previous:
                raise ValueError("opportunity funnel stages must be cumulative")

    def rate(self, value: int) -> float | None:
        if not self.candidate_cycles:
            return None
        return value / self.candidate_cycles

    def to_payload(self) -> dict[str, Any]:
        counts = {
            "candidate_cycles": self.candidate_cycles,
            "complete_evidence": self.complete_evidence,
            "structural_constraints_pass": self.structural_constraints_pass,
            "gross_positive": self.gross_positive,
            "net_positive": self.net_positive,
            "execute_threshold_eligible": self.execute_threshold_eligible,
            "final_execute_sim": self.final_execute_sim,
            "resolved_execute_outcomes": self.resolved_execute_outcomes,
            "truth_outcomes": self.truth_outcomes,
            "survived_required_edge": self.survived_required_edge,
        }
        return {
            "counts": counts,
            "rates_from_candidates": {
                name: self.rate(value) for name, value in counts.items()
            },
        }


@dataclass(frozen=True, slots=True)
class OpportunityFunnelSlice:
    key: str
    counts: OpportunityFunnelCounts
    gross_edge: FunnelDistribution
    expected_net_edge: FunnelDistribution
    observed_edge: FunnelDistribution
    modeled_cost_drag: FunnelDistribution

    def __post_init__(self) -> None:
        if not isinstance(self.key, str) or not self.key:
            raise ValueError("funnel slice key must be non-empty")
        if not isinstance(self.counts, OpportunityFunnelCounts):
            raise ValueError("funnel slice counts have invalid type")
        for value in (
            self.gross_edge,
            self.expected_net_edge,
            self.observed_edge,
            self.modeled_cost_drag,
        ):
            if not isinstance(value, FunnelDistribution):
                raise ValueError("funnel slice distribution has invalid type")
        if self.gross_edge.count != self.counts.candidate_cycles:
            raise ValueError("gross-edge coverage must equal candidate count")
        if self.expected_net_edge.count != self.counts.candidate_cycles:
            raise ValueError("expected-net coverage must equal candidate count")
        if self.modeled_cost_drag.count != self.counts.candidate_cycles:
            raise ValueError("modeled-cost coverage must equal candidate count")
        if self.observed_edge.count > self.counts.candidate_cycles:
            raise ValueError("observed-edge coverage cannot exceed candidate count")

    def to_payload(self) -> dict[str, Any]:
        return {
            "key": self.key,
            "funnel": self.counts.to_payload(),
            "gross_edge_bps": self.gross_edge.to_payload(),
            "expected_net_edge_bps": self.expected_net_edge.to_payload(),
            "observed_edge_bps": self.observed_edge.to_payload(),
            "modeled_cost_drag_bps": self.modeled_cost_drag.to_payload(),
        }


@dataclass(frozen=True, slots=True)
class _FunnelRow:
    operation_id: str
    route_id: str
    regime: str
    gross_edge_bps: float
    expected_net_edge_bps: float
    observed_edge_bps: float | None
    modeled_cost_drag_bps: float
    complete_evidence: bool
    structural_pass: bool
    gross_positive: bool
    net_positive: bool
    threshold_eligible: bool
    final_execute_sim: bool
    resolved_execute_outcome: bool
    truth_outcome: bool
    survived_required_edge: bool
    first_blocker: str
    structural_blockers: tuple[str, ...]
    economic_blockers: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class OpportunityFunnelReport:
    evidence_source: OpportunityTruthEvidenceSource
    source_sha256: str
    replay_bundle_sha256: str
    operation_ids: tuple[str, ...]
    overall: OpportunityFunnelSlice
    first_blocker_counts: tuple[tuple[str, int], ...]
    structural_blocker_counts: tuple[tuple[str, int], ...]
    economic_blocker_counts: tuple[tuple[str, int], ...]
    by_regime: tuple[OpportunityFunnelSlice, ...]
    by_route: tuple[OpportunityFunnelSlice, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.evidence_source, OpportunityTruthEvidenceSource):
            raise ValueError("evidence_source has invalid type")
        _sha(self.source_sha256, "source_sha256")
        _sha(self.replay_bundle_sha256, "replay_bundle_sha256")
        object.__setattr__(self, "operation_ids", tuple(self.operation_ids))
        if self.operation_ids != tuple(sorted(set(self.operation_ids))):
            raise ValueError("operation_ids must be sorted and unique")
        if not isinstance(self.overall, OpportunityFunnelSlice):
            raise ValueError("overall funnel slice has invalid type")
        if self.overall.key != "ALL":
            raise ValueError("overall funnel slice key must be ALL")
        if self.overall.counts.candidate_cycles != len(self.operation_ids):
            raise ValueError("operation membership differs from candidate count")

        for name in (
            "first_blocker_counts",
            "structural_blocker_counts",
            "economic_blocker_counts",
        ):
            rows = tuple(getattr(self, name))
            object.__setattr__(self, name, rows)
            if rows != tuple(sorted(rows)):
                raise ValueError(f"{name} must be sorted")
            for key, value in rows:
                if not isinstance(key, str) or not key:
                    raise ValueError(f"{name} contains an empty key")
                if _count(value, f"{name} count") < 1:
                    raise ValueError(f"{name} counts must be positive")
        if sum(value for _, value in self.first_blocker_counts) != len(
            self.operation_ids
        ):
            raise ValueError("first blocker coverage must equal candidate count")

        object.__setattr__(self, "by_regime", tuple(self.by_regime))
        object.__setattr__(self, "by_route", tuple(self.by_route))
        for name, rows in (("by_regime", self.by_regime), ("by_route", self.by_route)):
            keys = tuple(row.key for row in rows)
            if keys != tuple(sorted(set(keys))):
                raise ValueError(f"{name} keys must be sorted and unique")
            if sum(row.counts.candidate_cycles for row in rows) != len(
                self.operation_ids
            ):
                raise ValueError(f"{name} coverage must equal candidate count")

    def canonical_payload(self) -> dict[str, Any]:
        return {
            "schema": _SCHEMA,
            "evidence_source": self.evidence_source.value,
            "source_sha256": self.source_sha256,
            "replay_bundle_sha256": self.replay_bundle_sha256,
            "operation_ids": list(self.operation_ids),
            "overall": self.overall.to_payload(),
            "first_blocker_counts": [
                {"reason": reason, "count": count}
                for reason, count in self.first_blocker_counts
            ],
            "structural_blocker_counts": [
                {"reason": reason, "count": count}
                for reason, count in self.structural_blocker_counts
            ],
            "economic_blocker_counts": [
                {"reason": reason, "count": count}
                for reason, count in self.economic_blocker_counts
            ],
            "by_regime": [item.to_payload() for item in self.by_regime],
            "by_route": [item.to_payload() for item in self.by_route],
            "gross_positive_is_not_execution_permission": True,
            "empty_downstream_stage_is_valid_evidence": True,
            "rejected_routes_are_not_false_positives": True,
            "diagnostic_only": True,
            "paper_only": True,
        }

    @property
    def sha256(self) -> str:
        return _digest(self.canonical_payload())

    def to_envelope(self) -> dict[str, Any]:
        return {"payload": self.canonical_payload(), "sha256": self.sha256}


def _first_structural_blocker(reasons: Sequence[str]) -> str | None:
    structural = sorted(reason for reason in reasons if _is_structural_reason(reason))
    return structural[0] if structural else None


def _build_row(case: ReplayCase) -> _FunnelRow:
    route = case.build_route()
    base = evaluate_route(route, case.start_amount, policy=case.engine_policy)
    result = replay_case(case)

    gross_edge_bps = base.gross_edge * 10_000.0
    expected_net_edge_bps = base.net_edge * 10_000.0
    observed_edge_bps = result.observed_edge_bps
    cost_drag = gross_edge_bps - expected_net_edge_bps
    if cost_drag < -1e-9:
        raise ValueError("modeled execution costs cannot improve route edge")

    complete = result.regime is not MarketRegime.UNKNOWN
    structural_reasons = tuple(
        sorted(reason for reason in base.reasons if _is_structural_reason(reason))
    )
    structural_pass = complete and not structural_reasons
    gross_positive = structural_pass and gross_edge_bps > 0.0
    net_positive = gross_positive and expected_net_edge_bps > 0.0
    threshold_bps = case.engine_policy.execute_net_edge * 10_000.0
    threshold_eligible = net_positive and expected_net_edge_bps >= threshold_bps
    final_execute = (
        threshold_eligible and result.expected_verdict is Verdict.EXECUTE_SIM
    )
    resolved = final_execute and result.outcome_class in {
        OutcomeClass.TRUE_POSITIVE,
        OutcomeClass.FALSE_POSITIVE,
        OutcomeClass.EXPIRED,
    }
    truth = final_execute and result.outcome_class in {
        OutcomeClass.TRUE_POSITIVE,
        OutcomeClass.FALSE_POSITIVE,
    }
    survived = final_execute and result.outcome_class is OutcomeClass.TRUE_POSITIVE

    structural_blockers: tuple[str, ...] = ()
    economic_blockers: tuple[str, ...] = ()
    if not complete:
        structural_blockers = ("INCOMPLETE_EVIDENCE",)
        first = "INCOMPLETE_EVIDENCE"
    elif structural_reasons:
        structural_blockers = structural_reasons
        first = f"STRUCTURAL:{_first_structural_blocker(structural_reasons)}"
    elif not gross_positive:
        economic_blockers = ("GROSS_NON_POSITIVE",)
        first = "GROSS_NON_POSITIVE"
    elif not net_positive:
        economic_blockers = ("MODELED_COSTS_ERASE_EDGE",)
        first = "MODELED_COSTS_ERASE_EDGE"
    elif not threshold_eligible:
        economic_blockers = ("BELOW_EXECUTE_THRESHOLD",)
        first = "BELOW_EXECUTE_THRESHOLD"
    elif not final_execute:
        blocker = f"REGIME_GATE_DOWNGRADE:{result.regime.value}:{result.regime_action.value}"
        economic_blockers = (blocker,)
        first = blocker
    elif result.outcome_class is OutcomeClass.EXPIRED:
        economic_blockers = ("EXPIRED_BEFORE_REALIZED_OUTCOME",)
        first = "EXPIRED_BEFORE_REALIZED_OUTCOME"
    elif result.outcome_class is OutcomeClass.INDETERMINATE:
        economic_blockers = ("MISSING_REALIZED_OUTCOME",)
        first = "MISSING_REALIZED_OUTCOME"
    elif result.outcome_class is OutcomeClass.FALSE_POSITIVE:
        economic_blockers = ("FAILED_REQUIRED_EDGE",)
        first = "FAILED_REQUIRED_EDGE"
    elif result.outcome_class is OutcomeClass.TRUE_POSITIVE:
        first = "SURVIVED_REQUIRED_EDGE"
    else:
        raise ValueError("unexpected funnel outcome class")

    return _FunnelRow(
        operation_id=case.logical_operation_id,
        route_id=result.route_id,
        regime=result.regime.value,
        gross_edge_bps=gross_edge_bps,
        expected_net_edge_bps=expected_net_edge_bps,
        observed_edge_bps=observed_edge_bps,
        modeled_cost_drag_bps=max(0.0, cost_drag),
        complete_evidence=complete,
        structural_pass=structural_pass,
        gross_positive=gross_positive,
        net_positive=net_positive,
        threshold_eligible=threshold_eligible,
        final_execute_sim=final_execute,
        resolved_execute_outcome=resolved,
        truth_outcome=truth,
        survived_required_edge=survived,
        first_blocker=first,
        structural_blockers=structural_blockers,
        economic_blockers=economic_blockers,
    )


def _slice(key: str, rows: Sequence[_FunnelRow]) -> OpportunityFunnelSlice:
    rows = tuple(rows)
    counts = OpportunityFunnelCounts(
        candidate_cycles=len(rows),
        complete_evidence=sum(row.complete_evidence for row in rows),
        structural_constraints_pass=sum(row.structural_pass for row in rows),
        gross_positive=sum(row.gross_positive for row in rows),
        net_positive=sum(row.net_positive for row in rows),
        execute_threshold_eligible=sum(row.threshold_eligible for row in rows),
        final_execute_sim=sum(row.final_execute_sim for row in rows),
        resolved_execute_outcomes=sum(
            row.resolved_execute_outcome for row in rows
        ),
        truth_outcomes=sum(row.truth_outcome for row in rows),
        survived_required_edge=sum(row.survived_required_edge for row in rows),
    )
    return OpportunityFunnelSlice(
        key=key,
        counts=counts,
        gross_edge=FunnelDistribution.from_values(
            [row.gross_edge_bps for row in rows]
        ),
        expected_net_edge=FunnelDistribution.from_values(
            [row.expected_net_edge_bps for row in rows]
        ),
        observed_edge=FunnelDistribution.from_values(
            [
                row.observed_edge_bps
                for row in rows
                if row.observed_edge_bps is not None
            ]
        ),
        modeled_cost_drag=FunnelDistribution.from_values(
            [row.modeled_cost_drag_bps for row in rows]
        ),
    )


def build_opportunity_funnel(
    source: RealMarketReplayCorpus | ReplayBundle,
) -> OpportunityFunnelReport:
    if isinstance(source, RealMarketReplayCorpus):
        evidence_source = OpportunityTruthEvidenceSource.REAL_MARKET_CORPUS
        source_sha = source.sha256
        bundle = source.to_replay_bundle()
    elif isinstance(source, ReplayBundle):
        evidence_source = OpportunityTruthEvidenceSource.REPLAY_BUNDLE
        source_sha = source.sha256
        bundle = source
    else:
        raise ValueError("source must be RealMarketReplayCorpus or ReplayBundle")

    terminal_cases = tuple(
        case for case in bundle.collapsed_cases() if case.outcome.terminal
    )
    rows = tuple(_build_row(case) for case in terminal_cases)

    first: Counter[str] = Counter(row.first_blocker for row in rows)
    structural: Counter[str] = Counter()
    economic: Counter[str] = Counter()
    by_regime: dict[str, list[_FunnelRow]] = defaultdict(list)
    by_route: dict[str, list[_FunnelRow]] = defaultdict(list)
    for row in rows:
        structural.update(row.structural_blockers)
        economic.update(row.economic_blockers)
        by_regime[row.regime].append(row)
        by_route[row.route_id].append(row)

    return OpportunityFunnelReport(
        evidence_source=evidence_source,
        source_sha256=source_sha,
        replay_bundle_sha256=bundle.sha256,
        operation_ids=tuple(sorted(row.operation_id for row in rows)),
        overall=_slice("ALL", rows),
        first_blocker_counts=tuple(sorted(first.items())),
        structural_blocker_counts=tuple(sorted(structural.items())),
        economic_blocker_counts=tuple(sorted(economic.items())),
        by_regime=tuple(
            _slice(key, by_regime[key]) for key in sorted(by_regime)
        ),
        by_route=tuple(_slice(key, by_route[key]) for key in sorted(by_route)),
    )


def verify_opportunity_funnel_envelope(
    envelope: Mapping[str, Any],
    *,
    source: RealMarketReplayCorpus | ReplayBundle,
) -> bool:
    if not isinstance(envelope, Mapping) or set(envelope) != {"payload", "sha256"}:
        raise ValueError("opportunity funnel envelope is not canonical")
    payload = envelope["payload"]
    supplied_sha = envelope["sha256"]
    if not isinstance(payload, dict) or payload.get("schema") != _SCHEMA:
        raise ValueError("unsupported opportunity funnel schema")
    for flag in (
        "gross_positive_is_not_execution_permission",
        "empty_downstream_stage_is_valid_evidence",
        "rejected_routes_are_not_false_positives",
        "diagnostic_only",
        "paper_only",
    ):
        if payload.get(flag) is not True:
            raise ValueError(f"opportunity funnel invariant is invalid: {flag}")
    if not isinstance(supplied_sha, str) or not hmac.compare_digest(
        _digest(payload), supplied_sha
    ):
        raise ValueError("opportunity funnel SHA-256 does not match payload")
    rebuilt = build_opportunity_funnel(source)
    if rebuilt.canonical_payload() != payload:
        raise ValueError("opportunity funnel does not reproduce from source")
    if not hmac.compare_digest(rebuilt.sha256, supplied_sha):
        raise ValueError("opportunity funnel digest differs after reproduction")
    return True


def render_opportunity_funnel_markdown(report: OpportunityFunnelReport) -> str:
    counts = report.overall.counts

    def pct(value: int) -> str:
        rate = counts.rate(value)
        return "n/a" if rate is None else f"{rate * 100:.2f}%"

    def stats(value: FunnelDistribution) -> str:
        if value.count == 0:
            return "n/a"
        return (
            f"mean {value.mean_bps:.2f} bps "
            f"(min {value.minimum_bps:.2f}, max {value.maximum_bps:.2f})"
        )

    lines = [
        "# RESONANCE Verify — Opportunity Funnel Benchmark",
        "",
        f"- Evidence source: **{report.evidence_source.value}**",
        f"- Source SHA-256: `{report.source_sha256}`",
        f"- Replay SHA-256: `{report.replay_bundle_sha256}`",
        "",
        "## Cumulative funnel",
        "",
        f"- Captured terminal cycles: **{counts.candidate_cycles}**",
        f"- Complete evidence: **{counts.complete_evidence}** ({pct(counts.complete_evidence)})",
        f"- Structural constraints pass: **{counts.structural_constraints_pass}** ({pct(counts.structural_constraints_pass)})",
        f"- Gross-positive before costs: **{counts.gross_positive}** ({pct(counts.gross_positive)})",
        f"- Net-positive after modeled costs: **{counts.net_positive}** ({pct(counts.net_positive)})",
        f"- Execute-threshold eligible: **{counts.execute_threshold_eligible}** ({pct(counts.execute_threshold_eligible)})",
        f"- Final EXECUTE_SIM: **{counts.final_execute_sim}** ({pct(counts.final_execute_sim)})",
        f"- Resolved execute outcomes: **{counts.resolved_execute_outcomes}** ({pct(counts.resolved_execute_outcomes)})",
        f"- TP + FP truth outcomes: **{counts.truth_outcomes}** ({pct(counts.truth_outcomes)})",
        f"- Survived required edge: **{counts.survived_required_edge}** ({pct(counts.survived_required_edge)})",
        "",
        "## Edge distributions",
        "",
        f"- Gross edge: **{stats(report.overall.gross_edge)}**",
        f"- Expected net edge: **{stats(report.overall.expected_net_edge)}**",
        f"- Observed terminal edge: **{stats(report.overall.observed_edge)}**",
        f"- Modeled cost drag: **{stats(report.overall.modeled_cost_drag)}**",
        "",
        "## Interpretation boundary",
        "",
        "Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.",
    ]
    if counts.final_execute_sim == 0:
        lines.extend(
            [
                "",
                "**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.",
            ]
        )
    if report.first_blocker_counts:
        lines.extend(["", "## First blocker", ""])
        for reason, count in sorted(
            report.first_blocker_counts,
            key=lambda item: (-item[1], item[0]),
        ):
            lines.append(f"- {count} × `{reason}`")
    lines.extend(["", f"Evidence SHA-256: `{report.sha256}`", ""])
    return "\n".join(lines)
