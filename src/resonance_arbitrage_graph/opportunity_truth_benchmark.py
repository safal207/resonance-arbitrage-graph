from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from enum import Enum
import hashlib
import hmac
import json
from typing import Any

from .model import Verdict
from .real_market_corpus import RealMarketReplayCorpus
from .replay import ReplayBundle, ReplayMetrics, ReplayResult, benchmark_bundle


_SCHEMA = "resonance.verify.opportunity-truth-benchmark/v0.1"


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


def _positive_int(value: Any, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError(f"{name} must be an integer >= 1")
    return value


def _sha256_text(value: Any, name: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise ValueError(f"{name} must be a 64-character SHA-256 hex digest")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{name} must be hexadecimal") from exc
    if value.lower() != value:
        raise ValueError(f"{name} must be lowercase")
    return value


class OpportunityTruthBenchmarkStatus(str, Enum):
    READY = "READY"
    INSUFFICIENT_TRUTH_POPULATION = "INSUFFICIENT_TRUTH_POPULATION"


class OpportunityTruthEvidenceSource(str, Enum):
    REPLAY_BUNDLE = "REPLAY_BUNDLE"
    REAL_MARKET_CORPUS = "REAL_MARKET_CORPUS"


@dataclass(frozen=True, slots=True)
class OpportunityTruthBenchmarkSlice:
    key: str
    logical_operations: int
    execute_sim_decisions: int
    metrics: ReplayMetrics
    realized_paper_pnl: float
    evaluated_execute_sim_capital: float

    def __post_init__(self) -> None:
        if not isinstance(self.key, str) or not self.key:
            raise ValueError("benchmark slice key must be non-empty")
        for name in ("logical_operations", "execute_sim_decisions"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise ValueError(f"{name} must be a non-negative integer")
        if not isinstance(self.metrics, ReplayMetrics):
            raise ValueError("benchmark slice metrics must be ReplayMetrics")
        if self.execute_sim_decisions > self.logical_operations:
            raise ValueError("execute_sim_decisions cannot exceed logical_operations")

    @property
    def realized_paper_return_bps(self) -> float | None:
        if self.evaluated_execute_sim_capital <= 0:
            return None
        return self.realized_paper_pnl / self.evaluated_execute_sim_capital * 10_000.0

    def to_payload(self) -> dict[str, Any]:
        return {
            "key": self.key,
            "logical_operations": self.logical_operations,
            "execute_sim_decisions": self.execute_sim_decisions,
            "metrics": self.metrics.to_payload(),
            "realized_paper_pnl": self.realized_paper_pnl,
            "evaluated_execute_sim_capital": self.evaluated_execute_sim_capital,
            "realized_paper_return_bps": self.realized_paper_return_bps,
        }


@dataclass(frozen=True, slots=True)
class OpportunityTruthBenchmarkReport:
    source_bundle_sha256: str
    evidence_source: OpportunityTruthEvidenceSource
    source_corpus_sha256: str | None
    min_truth_population: int
    status: OpportunityTruthBenchmarkStatus
    candidate_opportunities: int
    execute_sim_decisions: int
    observe_decisions: int
    reject_decisions: int
    truth_population: int
    metrics: ReplayMetrics
    realized_paper_pnl: float
    evaluated_execute_sim_capital: float
    downgrade_reason_counts: tuple[tuple[str, int], ...]
    by_regime: tuple[OpportunityTruthBenchmarkSlice, ...]
    by_route: tuple[OpportunityTruthBenchmarkSlice, ...]

    def __post_init__(self) -> None:
        _sha256_text(self.source_bundle_sha256, "source_bundle_sha256")
        if not isinstance(self.evidence_source, OpportunityTruthEvidenceSource):
            raise ValueError("evidence_source has invalid type")
        if self.evidence_source is OpportunityTruthEvidenceSource.REAL_MARKET_CORPUS:
            _sha256_text(self.source_corpus_sha256, "source_corpus_sha256")
        elif self.source_corpus_sha256 is not None:
            raise ValueError("replay-bundle source cannot claim a real-market corpus digest")
        _positive_int(self.min_truth_population, "min_truth_population")
        if not isinstance(self.status, OpportunityTruthBenchmarkStatus):
            raise ValueError("benchmark status has invalid type")
        if not isinstance(self.metrics, ReplayMetrics):
            raise ValueError("benchmark metrics must be ReplayMetrics")
        for name in (
            "candidate_opportunities",
            "execute_sim_decisions",
            "observe_decisions",
            "reject_decisions",
            "truth_population",
        ):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise ValueError(f"{name} must be a non-negative integer")
        if self.candidate_opportunities != (
            self.execute_sim_decisions + self.observe_decisions + self.reject_decisions
        ):
            raise ValueError("benchmark verdict counts must cover every candidate")
        expected_truth_population = self.metrics.true_positive + self.metrics.false_positive
        if self.truth_population != expected_truth_population:
            raise ValueError("truth_population does not match replay metrics")
        expected_status = (
            OpportunityTruthBenchmarkStatus.READY
            if self.truth_population >= self.min_truth_population
            else OpportunityTruthBenchmarkStatus.INSUFFICIENT_TRUTH_POPULATION
        )
        if self.status is not expected_status:
            raise ValueError("benchmark status does not match sample-size guardrail")
        object.__setattr__(self, "downgrade_reason_counts", tuple(self.downgrade_reason_counts))
        object.__setattr__(self, "by_regime", tuple(self.by_regime))
        object.__setattr__(self, "by_route", tuple(self.by_route))
        if tuple(sorted(self.downgrade_reason_counts)) != self.downgrade_reason_counts:
            raise ValueError("downgrade reason counts must be sorted")

    @property
    def realized_paper_return_bps(self) -> float | None:
        if self.evaluated_execute_sim_capital <= 0:
            return None
        return self.realized_paper_pnl / self.evaluated_execute_sim_capital * 10_000.0

    @property
    def sample_size_gate_passed(self) -> bool:
        return self.status is OpportunityTruthBenchmarkStatus.READY

    @property
    def public_claim_eligible(self) -> bool:
        return (
            self.sample_size_gate_passed
            and self.evidence_source is OpportunityTruthEvidenceSource.REAL_MARKET_CORPUS
            and self.source_corpus_sha256 is not None
        )

    def canonical_payload(self) -> dict[str, Any]:
        return {
            "schema": _SCHEMA,
            "source_bundle_sha256": self.source_bundle_sha256,
            "evidence_source": self.evidence_source.value,
            "source_corpus_sha256": self.source_corpus_sha256,
            "min_truth_population": self.min_truth_population,
            "status": self.status.value,
            "candidate_opportunities": self.candidate_opportunities,
            "execute_sim_decisions": self.execute_sim_decisions,
            "observe_decisions": self.observe_decisions,
            "reject_decisions": self.reject_decisions,
            "truth_population": self.truth_population,
            "metrics": self.metrics.to_payload(),
            "realized_paper_pnl": self.realized_paper_pnl,
            "evaluated_execute_sim_capital": self.evaluated_execute_sim_capital,
            "realized_paper_return_bps": self.realized_paper_return_bps,
            "downgrade_reason_counts": [
                {"reason": reason, "count": count}
                for reason, count in self.downgrade_reason_counts
            ],
            "by_regime": [item.to_payload() for item in self.by_regime],
            "by_route": [item.to_payload() for item in self.by_route],
            "sample_size_gate_passed": self.sample_size_gate_passed,
            "public_claim_eligible": self.public_claim_eligible,
            "marketing_claims_must_use_real_corpus_only": True,
            "paper_only": True,
        }

    @property
    def sha256(self) -> str:
        return _sha256(self.canonical_payload())

    def to_envelope(self) -> dict[str, Any]:
        return {"payload": self.canonical_payload(), "sha256": self.sha256}


def _paper_pnl(
    results: Sequence[ReplayResult],
    cases_by_operation: Mapping[str, Any],
) -> tuple[float, float]:
    pnl = 0.0
    capital = 0.0
    for result in results:
        if result.expected_verdict is not Verdict.EXECUTE_SIM:
            continue
        if result.observed_edge_bps is None:
            continue
        case = cases_by_operation[result.logical_operation_id]
        capital += case.start_amount
        pnl += case.start_amount * result.observed_edge_bps / 10_000.0
    return pnl, capital


def _slice(
    key: str,
    results: Sequence[ReplayResult],
    metrics: ReplayMetrics,
    cases_by_operation: Mapping[str, Any],
) -> OpportunityTruthBenchmarkSlice:
    pnl, capital = _paper_pnl(results, cases_by_operation)
    return OpportunityTruthBenchmarkSlice(
        key=key,
        logical_operations=len(results),
        execute_sim_decisions=sum(
            result.expected_verdict is Verdict.EXECUTE_SIM for result in results
        ),
        metrics=metrics,
        realized_paper_pnl=pnl,
        evaluated_execute_sim_capital=capital,
    )


def _build(
    bundle: ReplayBundle,
    *,
    min_truth_population: int,
    evidence_source: OpportunityTruthEvidenceSource,
    source_corpus_sha256: str | None,
) -> OpportunityTruthBenchmarkReport:
    _positive_int(min_truth_population, "min_truth_population")
    calibration = benchmark_bundle(bundle)
    results = calibration.results
    collapsed = bundle.collapsed_cases()
    cases_by_operation = {case.logical_operation_id: case for case in collapsed}

    execute_sim = sum(result.expected_verdict is Verdict.EXECUTE_SIM for result in results)
    observe = sum(result.expected_verdict is Verdict.OBSERVE for result in results)
    reject = sum(result.expected_verdict is Verdict.REJECT for result in results)
    truth_population = calibration.overall.true_positive + calibration.overall.false_positive

    reason_counts: Counter[str] = Counter()
    for result in results:
        if result.expected_verdict is Verdict.EXECUTE_SIM:
            continue
        reason_counts.update(result.reasons)

    regime_groups: dict[str, list[ReplayResult]] = defaultdict(list)
    route_groups: dict[str, list[ReplayResult]] = defaultdict(list)
    for result in results:
        regime_groups[result.regime.value].append(result)
        route_groups[result.route_id].append(result)

    metrics_by_regime = {item.key: item.metrics for item in calibration.by_regime}
    metrics_by_route = {item.key: item.metrics for item in calibration.by_route}
    pnl, capital = _paper_pnl(results, cases_by_operation)

    return OpportunityTruthBenchmarkReport(
        source_bundle_sha256=bundle.sha256,
        evidence_source=evidence_source,
        source_corpus_sha256=source_corpus_sha256,
        min_truth_population=min_truth_population,
        status=(
            OpportunityTruthBenchmarkStatus.READY
            if truth_population >= min_truth_population
            else OpportunityTruthBenchmarkStatus.INSUFFICIENT_TRUTH_POPULATION
        ),
        candidate_opportunities=len(results),
        execute_sim_decisions=execute_sim,
        observe_decisions=observe,
        reject_decisions=reject,
        truth_population=truth_population,
        metrics=calibration.overall,
        realized_paper_pnl=pnl,
        evaluated_execute_sim_capital=capital,
        downgrade_reason_counts=tuple(sorted(reason_counts.items())),
        by_regime=tuple(
            _slice(key, regime_groups[key], metrics_by_regime[key], cases_by_operation)
            for key in sorted(regime_groups)
        ),
        by_route=tuple(
            _slice(key, route_groups[key], metrics_by_route[key], cases_by_operation)
            for key in sorted(route_groups)
        ),
    )


def build_opportunity_truth_benchmark(
    bundle: ReplayBundle,
    *,
    min_truth_population: int = 30,
) -> OpportunityTruthBenchmarkReport:
    if not isinstance(bundle, ReplayBundle):
        raise ValueError("benchmark requires ReplayBundle")
    return _build(
        bundle,
        min_truth_population=min_truth_population,
        evidence_source=OpportunityTruthEvidenceSource.REPLAY_BUNDLE,
        source_corpus_sha256=None,
    )


def build_opportunity_truth_benchmark_from_corpus(
    corpus: RealMarketReplayCorpus,
    *,
    min_truth_population: int = 30,
) -> OpportunityTruthBenchmarkReport:
    if not isinstance(corpus, RealMarketReplayCorpus):
        raise ValueError("real-market benchmark requires RealMarketReplayCorpus")
    bundle = corpus.to_replay_bundle()
    return _build(
        bundle,
        min_truth_population=min_truth_population,
        evidence_source=OpportunityTruthEvidenceSource.REAL_MARKET_CORPUS,
        source_corpus_sha256=corpus.sha256,
    )


def render_opportunity_truth_markdown(report: OpportunityTruthBenchmarkReport) -> str:
    def pct(value: float | None) -> str:
        return "n/a" if value is None else f"{value * 100:.2f}%"

    def num(value: float | None, suffix: str = "") -> str:
        return "n/a" if value is None else f"{value:.2f}{suffix}"

    if not report.sample_size_gate_passed:
        readiness = "NOT READY — INSUFFICIENT DETERMINATE EXECUTE_SIM OUTCOMES"
    elif not report.public_claim_eligible:
        readiness = "SAMPLE READY — NOT ELIGIBLE FOR PUBLIC CLAIMS (NON-CORPUS SOURCE)"
    else:
        readiness = "READY — REAL-MARKET SOURCE + SAMPLE-SIZE GATE PASSED"

    lines = [
        "# RESONANCE Verify — Opportunity Truth Benchmark",
        "",
        f"**Status:** {readiness}",
        "",
        f"- Evidence source: **{report.evidence_source.value}**",
        f"- Source corpus SHA-256: **{report.source_corpus_sha256 or 'n/a'}**",
        f"- Candidate opportunities: **{report.candidate_opportunities}**",
        f"- EXECUTE_SIM decisions: **{report.execute_sim_decisions}**",
        f"- Truth population (TP + FP): **{report.truth_population}** / required **{report.min_truth_population}**",
        f"- Opportunity Truth Rate: **{pct(report.metrics.opportunity_truth_rate)}**",
        f"- False Opportunity Rate: **{pct(report.metrics.false_opportunity_rate)}**",
        f"- Route Survival Rate: **{pct(report.metrics.route_survival_rate)}**",
        f"- Mean prediction error: **{num(report.metrics.mean_prediction_error_bps, ' bps')}**",
        f"- Realized paper PnL for evaluated EXECUTE_SIM decisions: **{num(report.realized_paper_pnl)}**",
        f"- Capital evaluated for that paper PnL: **{num(report.evaluated_execute_sim_capital)}**",
        f"- Capital-weighted realized paper return: **{num(report.realized_paper_return_bps, ' bps')}**",
        f"- Public claim eligible: **{str(report.public_claim_eligible).lower()}**",
        "",
        "## Outcome counts",
        "",
        f"- TRUE_POSITIVE: {report.metrics.true_positive}",
        f"- FALSE_POSITIVE: {report.metrics.false_positive}",
        f"- EXPIRED: {report.metrics.expired}",
        f"- REJECTED: {report.metrics.rejected}",
        f"- INDETERMINATE: {report.metrics.indeterminate}",
        "",
        "## Product-proof boundary",
        "",
        "This report is paper-only. A sample-size gate passing does not by itself establish profitability or statistical significance. Public claims require evidence_source=REAL_MARKET_CORPUS and the bound source corpus SHA-256.",
        "",
        f"Evidence SHA-256: `{report.sha256}`",
    ]
    if report.downgrade_reason_counts:
        lines.extend(["", "## Downgrade / rejection reasons", ""])
        for reason, count in sorted(
            report.downgrade_reason_counts,
            key=lambda item: (-item[1], item[0]),
        ):
            lines.append(f"- {count} × {reason}")
    return "\n".join(lines) + "\n"


def verify_opportunity_truth_benchmark_envelope(
    envelope: Mapping[str, Any],
    *,
    source: ReplayBundle | RealMarketReplayCorpus,
) -> bool:
    if not isinstance(envelope, Mapping) or set(envelope) != {"payload", "sha256"}:
        raise ValueError("benchmark envelope is not canonical")
    payload = envelope["payload"]
    supplied_sha = envelope["sha256"]
    if not isinstance(payload, dict) or payload.get("schema") != _SCHEMA:
        raise ValueError("unsupported opportunity truth benchmark schema")
    if not isinstance(supplied_sha, str) or not hmac.compare_digest(_sha256(payload), supplied_sha):
        raise ValueError("benchmark SHA-256 does not match payload")
    min_truth_population = _positive_int(payload.get("min_truth_population"), "min_truth_population")
    if isinstance(source, RealMarketReplayCorpus):
        rebuilt = build_opportunity_truth_benchmark_from_corpus(
            source,
            min_truth_population=min_truth_population,
        )
    elif isinstance(source, ReplayBundle):
        rebuilt = build_opportunity_truth_benchmark(
            source,
            min_truth_population=min_truth_population,
        )
    else:
        raise ValueError("benchmark verification requires ReplayBundle or RealMarketReplayCorpus")
    if rebuilt.canonical_payload() != payload:
        raise ValueError("benchmark report does not reproduce from supplied source evidence")
    if not hmac.compare_digest(rebuilt.sha256, supplied_sha):
        raise ValueError("benchmark digest differs after reproduction")
    return True
