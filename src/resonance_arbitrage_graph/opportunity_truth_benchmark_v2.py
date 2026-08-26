from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from enum import Enum
import hashlib
import hmac
import json
import math
from statistics import mean
from typing import Any

from .corpus_quality import CorpusQualityPolicy, build_corpus_quality_report
from .observation import OutcomeClass
from .opportunity_truth_benchmark import (
    OpportunityTruthBenchmarkReport,
    OpportunityTruthEvidenceSource,
    build_opportunity_truth_benchmark,
    build_opportunity_truth_benchmark_from_corpus,
    verify_opportunity_truth_benchmark_envelope,
)
from .real_market_corpus import RealMarketReplayCorpus
from .replay import ReplayBundle, ReplayResult, benchmark_bundle

_SCHEMA = "resonance.verify.opportunity-truth-benchmark/v0.2"
_POLICY_SCHEMA = "resonance.verify.opportunity-truth-claim-policy/v0.1"


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


def _int(value: Any, name: str, *, minimum: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ValueError(f"{name} must be an integer >= {minimum}")
    return value


def _number(value: Any, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be numeric")
    value = float(value)
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    return value


def _same(left: float, right: float) -> bool:
    return math.isclose(left, right, rel_tol=0.0, abs_tol=1e-12)


class OpportunityTruthClaimStatus(str, Enum):
    NOT_READY = "NOT_READY"
    INTERNAL_EVIDENCE_READY = "INTERNAL_EVIDENCE_READY"
    UNASSESSED_REPLAY_SOURCE = "UNASSESSED_REPLAY_SOURCE"


@dataclass(frozen=True, slots=True)
class OpportunityTruthClaimPolicy:
    min_terminal_operations: int = 100
    min_truth_events: int = 30
    require_corpus_quality: bool = True

    def __post_init__(self) -> None:
        _int(self.min_terminal_operations, "min_terminal_operations", minimum=1)
        _int(self.min_truth_events, "min_truth_events", minimum=1)
        if not isinstance(self.require_corpus_quality, bool):
            raise ValueError("require_corpus_quality must be boolean")

    def to_payload(self) -> dict[str, Any]:
        return {
            "schema": _POLICY_SCHEMA,
            "min_terminal_operations": self.min_terminal_operations,
            "min_truth_events": self.min_truth_events,
            "require_corpus_quality": self.require_corpus_quality,
            "interpretation": "INTERNAL_EVIDENCE_READINESS_ONLY",
        }

    @property
    def sha256(self) -> str:
        return _digest(self.to_payload())

    @classmethod
    def from_payload(
        cls, payload: Mapping[str, Any]
    ) -> "OpportunityTruthClaimPolicy":
        if (
            payload.get("schema") != _POLICY_SCHEMA
            or payload.get("interpretation")
            != "INTERNAL_EVIDENCE_READINESS_ONLY"
        ):
            raise ValueError("unsupported claim policy payload")
        policy = cls(
            min_terminal_operations=payload.get("min_terminal_operations"),
            min_truth_events=payload.get("min_truth_events"),
            require_corpus_quality=payload.get("require_corpus_quality"),
        )
        if policy.to_payload() != dict(payload):
            raise ValueError("claim policy payload is not canonical")
        return policy


@dataclass(frozen=True, slots=True)
class OpportunityTruthPnlSlice:
    start_state: str
    truth_events: int
    capital_units: float
    expected_pnl_units: float
    observed_pnl_units: float

    def __post_init__(self) -> None:
        if not isinstance(self.start_state, str) or not self.start_state:
            raise ValueError("start_state must be non-empty")
        _int(self.truth_events, "truth_events", minimum=1)
        _number(self.capital_units, "capital_units")
        _number(self.expected_pnl_units, "expected_pnl_units")
        _number(self.observed_pnl_units, "observed_pnl_units")
        if self.capital_units <= 0:
            raise ValueError("capital_units must be positive")

    @property
    def pnl_delta_units(self) -> float:
        return self.observed_pnl_units - self.expected_pnl_units

    @property
    def observed_return_bps(self) -> float:
        return self.observed_pnl_units / self.capital_units * 10_000.0

    def to_payload(self) -> dict[str, Any]:
        return {
            "start_state": self.start_state,
            "truth_events": self.truth_events,
            "capital_units": self.capital_units,
            "expected_pnl_units": self.expected_pnl_units,
            "observed_pnl_units": self.observed_pnl_units,
            "pnl_delta_units": self.pnl_delta_units,
            "observed_return_bps": self.observed_return_bps,
        }

    @classmethod
    def from_payload(
        cls, payload: Mapping[str, Any]
    ) -> "OpportunityTruthPnlSlice":
        row = cls(
            start_state=payload.get("start_state"),
            truth_events=payload.get("truth_events"),
            capital_units=payload.get("capital_units"),
            expected_pnl_units=payload.get("expected_pnl_units"),
            observed_pnl_units=payload.get("observed_pnl_units"),
        )
        if (
            set(payload) != set(row.to_payload())
            or not _same(payload.get("pnl_delta_units"), row.pnl_delta_units)
            or not _same(
                payload.get("observed_return_bps"), row.observed_return_bps
            )
        ):
            raise ValueError("paper PnL slice is not canonical")
        return row


def _claim_status(
    source: OpportunityTruthEvidenceSource,
    terminal: int,
    truth: int,
    quality: Mapping[str, Any] | None,
    policy: OpportunityTruthClaimPolicy,
) -> tuple[OpportunityTruthClaimStatus, tuple[str, ...]]:
    if source is OpportunityTruthEvidenceSource.REPLAY_BUNDLE:
        return (
            OpportunityTruthClaimStatus.UNASSESSED_REPLAY_SOURCE,
            ("real_market_corpus_provenance",),
        )
    if quality is None:
        raise ValueError("real-market benchmark requires corpus quality evidence")
    reasons: list[str] = []
    if terminal < policy.min_terminal_operations:
        reasons.append("terminal_operations")
    if truth < policy.min_truth_events:
        reasons.append("truth_events")
    if policy.require_corpus_quality and not quality.get("quality_ready"):
        reasons.extend(
            f"corpus_quality:{item}"
            for item in quality.get("failed_dimensions", [])
        )
    if reasons:
        return OpportunityTruthClaimStatus.NOT_READY, tuple(reasons)
    return OpportunityTruthClaimStatus.INTERNAL_EVIDENCE_READY, ()


@dataclass(frozen=True, slots=True)
class OpportunityTruthBenchmarkV2Report:
    evidence_source: OpportunityTruthEvidenceSource
    source_sha256: str
    replay_bundle_sha256: str
    operation_ids: tuple[str, ...]
    legacy_benchmark: Mapping[str, Any]
    legacy_benchmark_sha256: str
    claim_policy: OpportunityTruthClaimPolicy
    claim_status: OpportunityTruthClaimStatus
    claim_reasons: tuple[str, ...]
    corpus_quality: Mapping[str, Any] | None
    corpus_quality_sha256: str | None
    terminal_operations: int
    truth_population: int
    truth_coverage: float | None
    mean_expected_edge_bps: float | None
    mean_observed_edge_bps: float | None
    mean_edge_decay_bps: float | None
    paper_pnl_by_start_state: tuple[OpportunityTruthPnlSlice, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.evidence_source, OpportunityTruthEvidenceSource):
            raise ValueError("evidence_source has invalid type")
        _sha(self.source_sha256, "source_sha256")
        _sha(self.replay_bundle_sha256, "replay_bundle_sha256")
        _sha(self.legacy_benchmark_sha256, "legacy_benchmark_sha256")
        object.__setattr__(self, "operation_ids", tuple(self.operation_ids))
        if self.operation_ids != tuple(sorted(set(self.operation_ids))):
            raise ValueError("operation_ids must be sorted and unique")

        legacy = dict(self.legacy_benchmark)
        object.__setattr__(self, "legacy_benchmark", legacy)
        verify_opportunity_truth_benchmark_envelope(
            {
                "payload": legacy,
                "sha256": self.legacy_benchmark_sha256,
            }
        )
        if (
            legacy["source_bundle_sha256"] != self.replay_bundle_sha256
            or legacy["evidence_source"] != self.evidence_source.value
        ):
            raise ValueError("legacy benchmark binding differs")
        expected_corpus = (
            self.source_sha256
            if self.evidence_source
            is OpportunityTruthEvidenceSource.REAL_MARKET_CORPUS
            else None
        )
        if legacy["source_corpus_sha256"] != expected_corpus:
            raise ValueError("legacy corpus binding differs")
        if len(self.operation_ids) != legacy["candidate_opportunities"]:
            raise ValueError("operation membership differs from candidate count")

        if (
            not isinstance(self.claim_policy, OpportunityTruthClaimPolicy)
            or not isinstance(self.claim_status, OpportunityTruthClaimStatus)
        ):
            raise ValueError("claim policy/status has invalid type")
        object.__setattr__(self, "claim_reasons", tuple(self.claim_reasons))
        _int(self.terminal_operations, "terminal_operations")
        _int(self.truth_population, "truth_population")
        if self.truth_population != legacy["truth_population"]:
            raise ValueError("truth population differs from legacy benchmark")

        execute_sim = legacy["execute_sim_decisions"]
        expected_coverage = (
            self.truth_population / execute_sim if execute_sim else None
        )
        if self.truth_coverage is None or expected_coverage is None:
            if self.truth_coverage is not expected_coverage:
                raise ValueError("truth coverage is inconsistent")
        elif not _same(
            _number(self.truth_coverage, "truth_coverage"),
            expected_coverage,
        ):
            raise ValueError("truth coverage is inconsistent")

        edges = (
            self.mean_expected_edge_bps,
            self.mean_observed_edge_bps,
            self.mean_edge_decay_bps,
        )
        if self.truth_population:
            if any(item is None for item in edges):
                raise ValueError("truth events require edge means")
            assert self.mean_expected_edge_bps is not None
            assert self.mean_observed_edge_bps is not None
            assert self.mean_edge_decay_bps is not None
            if not _same(
                self.mean_edge_decay_bps,
                self.mean_expected_edge_bps - self.mean_observed_edge_bps,
            ):
                raise ValueError("edge decay is inconsistent")
        elif any(item is not None for item in edges):
            raise ValueError("edge means require truth events")
        for name, value in zip(
            (
                "mean_expected_edge_bps",
                "mean_observed_edge_bps",
                "mean_edge_decay_bps",
            ),
            edges,
            strict=True,
        ):
            if value is not None:
                _number(value, name)

        quality = None if self.corpus_quality is None else dict(self.corpus_quality)
        object.__setattr__(self, "corpus_quality", quality)
        if quality is None:
            if (
                self.corpus_quality_sha256 is not None
                or self.evidence_source
                is OpportunityTruthEvidenceSource.REAL_MARKET_CORPUS
            ):
                raise ValueError(
                    "real-market source requires corpus quality payload and SHA"
                )
        else:
            _sha(self.corpus_quality_sha256, "corpus_quality_sha256")
            if not hmac.compare_digest(
                _digest(quality), self.corpus_quality_sha256
            ):
                raise ValueError("corpus quality SHA differs")
            if (
                quality.get("corpus_sha256") != self.source_sha256
                or quality.get("terminal_operation_count")
                != self.terminal_operations
            ):
                raise ValueError("corpus quality source/count differs")
            if quality.get("quality_ready") is not (
                not quality.get("failed_dimensions")
            ):
                raise ValueError("corpus quality readiness is inconsistent")

        expected_status, expected_reasons = _claim_status(
            self.evidence_source,
            self.terminal_operations,
            self.truth_population,
            quality,
            self.claim_policy,
        )
        if (
            self.claim_status is not expected_status
            or self.claim_reasons != expected_reasons
        ):
            raise ValueError("claim status differs from bound evidence")

        object.__setattr__(
            self,
            "paper_pnl_by_start_state",
            tuple(self.paper_pnl_by_start_state),
        )
        states = tuple(
            item.start_state for item in self.paper_pnl_by_start_state
        )
        if (
            states != tuple(sorted(set(states)))
            or sum(
                item.truth_events for item in self.paper_pnl_by_start_state
            )
            != self.truth_population
        ):
            raise ValueError("paper PnL state/truth coverage is inconsistent")

    @property
    def internal_evidence_ready(self) -> bool:
        return (
            self.claim_status
            is OpportunityTruthClaimStatus.INTERNAL_EVIDENCE_READY
        )

    def canonical_payload(self) -> dict[str, Any]:
        return {
            "schema": _SCHEMA,
            "evidence_source": self.evidence_source.value,
            "source_sha256": self.source_sha256,
            "replay_bundle_sha256": self.replay_bundle_sha256,
            "operation_ids": list(self.operation_ids),
            "legacy_benchmark_sha256": self.legacy_benchmark_sha256,
            "legacy_benchmark": dict(self.legacy_benchmark),
            "claim_policy_sha256": self.claim_policy.sha256,
            "claim_policy": self.claim_policy.to_payload(),
            "claim_status": self.claim_status.value,
            "claim_reasons": list(self.claim_reasons),
            "corpus_quality_sha256": self.corpus_quality_sha256,
            "corpus_quality": self.corpus_quality,
            "terminal_operations": self.terminal_operations,
            "truth_population": self.truth_population,
            "truth_coverage": self.truth_coverage,
            "mean_expected_edge_bps": self.mean_expected_edge_bps,
            "mean_observed_edge_bps": self.mean_observed_edge_bps,
            "mean_edge_decay_bps": self.mean_edge_decay_bps,
            "paper_pnl_by_start_state": [
                item.to_payload()
                for item in self.paper_pnl_by_start_state
            ],
            "internal_evidence_ready": self.internal_evidence_ready,
            "automated_readiness_is_not_publication_approval": True,
            "legacy_cross_unit_pnl_is_not_used": True,
            "paper_only": True,
        }

    @property
    def sha256(self) -> str:
        return _digest(self.canonical_payload())

    def to_envelope(self) -> dict[str, Any]:
        return {"payload": self.canonical_payload(), "sha256": self.sha256}


def _truth(results: Sequence[ReplayResult]) -> tuple[ReplayResult, ...]:
    return tuple(
        item
        for item in results
        if item.outcome_class
        in {OutcomeClass.TRUE_POSITIVE, OutcomeClass.FALSE_POSITIVE}
    )


def _pnl(
    bundle: ReplayBundle,
    results: Sequence[ReplayResult],
) -> tuple[OpportunityTruthPnlSlice, ...]:
    cases = {
        case.logical_operation_id: case for case in bundle.collapsed_cases()
    }
    grouped: dict[str, list[tuple[float, float, float]]] = defaultdict(list)
    for result in results:
        if result.observed_edge_bps is None:
            raise ValueError("truth result is missing observed edge")
        case = cases[result.logical_operation_id]
        start = case.build_route()[0].src
        grouped[f"{start.venue}:{start.asset}"].append(
            (
                case.start_amount,
                case.start_amount * result.expected_edge_bps / 10_000.0,
                case.start_amount * result.observed_edge_bps / 10_000.0,
            )
        )
    return tuple(
        OpportunityTruthPnlSlice(
            state,
            len(grouped[state]),
            sum(row[0] for row in grouped[state]),
            sum(row[1] for row in grouped[state]),
            sum(row[2] for row in grouped[state]),
        )
        for state in sorted(grouped)
    )


def build_opportunity_truth_benchmark_v2(
    source: RealMarketReplayCorpus | ReplayBundle,
    *,
    claim_policy: OpportunityTruthClaimPolicy | None = None,
    quality_policy: CorpusQualityPolicy | None = None,
) -> OpportunityTruthBenchmarkV2Report:
    policy = claim_policy or OpportunityTruthClaimPolicy()
    if isinstance(source, RealMarketReplayCorpus):
        kind = OpportunityTruthEvidenceSource.REAL_MARKET_CORPUS
        source_sha = source.sha256
        bundle = source.to_replay_bundle()
        legacy = build_opportunity_truth_benchmark_from_corpus(
            source,
            min_truth_population=policy.min_truth_events,
        )
        quality_report = build_corpus_quality_report(
            source,
            policy=quality_policy or CorpusQualityPolicy(),
        )
        quality = quality_report.to_payload()
    elif isinstance(source, ReplayBundle):
        kind = OpportunityTruthEvidenceSource.REPLAY_BUNDLE
        source_sha = source.sha256
        bundle = source
        legacy = build_opportunity_truth_benchmark(
            source,
            min_truth_population=policy.min_truth_events,
        )
        quality_report = None
        quality = None
    else:
        raise ValueError("source must be RealMarketReplayCorpus or ReplayBundle")

    calibration = benchmark_bundle(bundle)
    truth = _truth(calibration.results)
    expected = (
        mean(item.expected_edge_bps for item in truth) if truth else None
    )
    observed = (
        mean(
            item.observed_edge_bps
            for item in truth
            if item.observed_edge_bps is not None
        )
        if truth
        else None
    )
    terminal = (
        quality_report.terminal_operation_count
        if quality_report is not None
        else sum(case.outcome.terminal for case in bundle.collapsed_cases())
    )
    status, reasons = _claim_status(
        kind,
        terminal,
        len(truth),
        quality,
        policy,
    )
    return OpportunityTruthBenchmarkV2Report(
        evidence_source=kind,
        source_sha256=source_sha,
        replay_bundle_sha256=bundle.sha256,
        operation_ids=tuple(
            sorted(
                case.logical_operation_id
                for case in bundle.collapsed_cases()
            )
        ),
        legacy_benchmark=legacy.canonical_payload(),
        legacy_benchmark_sha256=legacy.sha256,
        claim_policy=policy,
        claim_status=status,
        claim_reasons=reasons,
        corpus_quality=quality,
        corpus_quality_sha256=(
            quality_report.sha256 if quality_report is not None else None
        ),
        terminal_operations=terminal,
        truth_population=len(truth),
        truth_coverage=(
            len(truth) / legacy.execute_sim_decisions
            if legacy.execute_sim_decisions
            else None
        ),
        mean_expected_edge_bps=expected,
        mean_observed_edge_bps=observed,
        mean_edge_decay_bps=(expected - observed if truth else None),
        paper_pnl_by_start_state=_pnl(bundle, truth),
    )


def _from_payload(
    payload: Mapping[str, Any]
) -> OpportunityTruthBenchmarkV2Report:
    if (
        payload.get("schema") != _SCHEMA
        or payload.get("automated_readiness_is_not_publication_approval")
        is not True
        or payload.get("legacy_cross_unit_pnl_is_not_used") is not True
        or payload.get("paper_only") is not True
    ):
        raise ValueError("unsupported opportunity truth v0.2 payload")
    policy = OpportunityTruthClaimPolicy.from_payload(
        payload.get("claim_policy", {})
    )
    if payload.get("claim_policy_sha256") != policy.sha256:
        raise ValueError("claim policy SHA differs")
    try:
        report = OpportunityTruthBenchmarkV2Report(
            evidence_source=OpportunityTruthEvidenceSource(
                payload["evidence_source"]
            ),
            source_sha256=payload["source_sha256"],
            replay_bundle_sha256=payload["replay_bundle_sha256"],
            operation_ids=tuple(payload["operation_ids"]),
            legacy_benchmark=payload["legacy_benchmark"],
            legacy_benchmark_sha256=payload["legacy_benchmark_sha256"],
            claim_policy=policy,
            claim_status=OpportunityTruthClaimStatus(payload["claim_status"]),
            claim_reasons=tuple(payload["claim_reasons"]),
            corpus_quality=payload["corpus_quality"],
            corpus_quality_sha256=payload["corpus_quality_sha256"],
            terminal_operations=payload["terminal_operations"],
            truth_population=payload["truth_population"],
            truth_coverage=payload["truth_coverage"],
            mean_expected_edge_bps=payload["mean_expected_edge_bps"],
            mean_observed_edge_bps=payload["mean_observed_edge_bps"],
            mean_edge_decay_bps=payload["mean_edge_decay_bps"],
            paper_pnl_by_start_state=tuple(
                OpportunityTruthPnlSlice.from_payload(item)
                for item in payload["paper_pnl_by_start_state"]
            ),
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("invalid opportunity truth v0.2 payload") from exc
    if (
        payload.get("internal_evidence_ready")
        is not report.internal_evidence_ready
        or report.canonical_payload() != dict(payload)
    ):
        raise ValueError(
            "opportunity truth v0.2 payload is not canonical after reconstruction"
        )
    return report


def verify_opportunity_truth_benchmark_v2_envelope(
    envelope: Mapping[str, Any]
) -> dict[str, Any]:
    if (
        not isinstance(envelope, Mapping)
        or set(envelope) != {"payload", "sha256"}
    ):
        raise ValueError("opportunity truth v0.2 envelope is not canonical")
    report = _from_payload(envelope["payload"])
    if not hmac.compare_digest(
        report.sha256,
        _sha(envelope["sha256"], "benchmark_v2_sha256"),
    ):
        raise ValueError("opportunity truth v0.2 SHA differs")
    return dict(envelope["payload"])


def verify_opportunity_truth_benchmark_v2_source_binding(
    report: OpportunityTruthBenchmarkV2Report | Mapping[str, Any],
    source: RealMarketReplayCorpus | ReplayBundle,
) -> bool:
    bound = (
        report
        if isinstance(report, OpportunityTruthBenchmarkV2Report)
        else _from_payload(
            verify_opportunity_truth_benchmark_v2_envelope(report)
        )
    )
    quality_policy = (
        CorpusQualityPolicy.from_payload(
            bound.corpus_quality["policy_payload"]
        )
        if bound.corpus_quality is not None
        else None
    )
    rebuilt = build_opportunity_truth_benchmark_v2(
        source,
        claim_policy=bound.claim_policy,
        quality_policy=quality_policy,
    )
    if rebuilt.canonical_payload() != bound.canonical_payload():
        raise ValueError(
            "opportunity truth v0.2 report does not reproduce from source"
        )
    return True


def render_opportunity_truth_benchmark_v2_markdown(
    report: OpportunityTruthBenchmarkV2Report,
) -> str:
    metrics = report.legacy_benchmark["metrics"]

    def pct(value: float | None) -> str:
        return "n/a" if value is None else f"{value * 100:.2f}%"

    def num(value: float | None, suffix: str = "") -> str:
        return "n/a" if value is None else f"{value:.4f}{suffix}"

    lines = [
        "# RESONANCE Verify — Opportunity Truth Benchmark v0.2",
        "",
        f"- **Claim status:** `{report.claim_status.value}`",
        f"- **Evidence source:** `{report.evidence_source.value}`",
        f"- **Terminal operations:** {report.terminal_operations}",
        f"- **Determinate truth events:** {report.truth_population}",
        f"- **Truth coverage:** {pct(report.truth_coverage)}",
        f"- **Opportunity Truth Rate:** "
        f"{pct(metrics['opportunity_truth_rate'])}",
        f"- **False Opportunity Rate:** "
        f"{pct(metrics['false_opportunity_rate'])}",
        f"- **Route Survival Rate:** "
        f"{pct(metrics['route_survival_rate'])}",
        f"- **Mean expected edge:** "
        f"{num(report.mean_expected_edge_bps, ' bps')}",
        f"- **Mean observed edge:** "
        f"{num(report.mean_observed_edge_bps, ' bps')}",
        f"- **Mean edge decay:** "
        f"{num(report.mean_edge_decay_bps, ' bps')}",
        "",
    ]
    if report.claim_reasons:
        lines += [
            "**Readiness blockers:** "
            + ", ".join(
                f"`{item}`" for item in report.claim_reasons
            ),
            "",
        ]
    if report.paper_pnl_by_start_state:
        lines += [
            "## Paper PnL by exact starting state",
            "",
            "| Start state | Truth | Capital units | Expected PnL | "
            "Observed PnL | Delta | Return |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
        lines += [
            f"| `{row.start_state}` | {row.truth_events} | "
            f"{row.capital_units:.6f} | {row.expected_pnl_units:.6f} | "
            f"{row.observed_pnl_units:.6f} | {row.pnl_delta_units:.6f} | "
            f"{row.observed_return_bps:.4f} bps |"
            for row in report.paper_pnl_by_start_state
        ]
        lines.append("")
    lines += [
        "## Interpretation boundary",
        "",
        "`INTERNAL_EVIDENCE_READY` means automated quantity and corpus-quality "
        "gates passed. It is not publication approval, a live-fill result, a "
        "profitability guarantee, or permission to activate a trading policy. "
        "PnL units are never added across different starting assets or venues.",
        "",
    ]
    return "\n".join(lines)
