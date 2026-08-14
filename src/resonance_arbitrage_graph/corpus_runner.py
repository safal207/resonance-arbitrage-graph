from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
import hashlib
import json
import math
from pathlib import Path
import time
from typing import Any

from .corpus_quality import (
    CorpusQualityPolicy,
    CorpusQualityReport,
    build_corpus_quality_report,
)
from .engine import Policy
from .live_scan import _collect_rolling_quotes, _fetch_round
from .model import Node
from .quotes import CostAssumption, QuoteSnapshot
from .real_market_corpus import (
    RealMarketReplayCorpus,
    build_decision_cases,
    export_replay_bundle,
    load_corpus,
    resolve_replay_case,
    save_corpus,
)
from .regime import RegimePolicy
from .regime_gate import RegimeExecutionPolicy
from .replay import ReplayBundle
from .rolling_state import RollingMarketWindow, RollingWindowPolicy
from .scanner import scan_cycles


_RUN_RECEIPT_SCHEMA = "resonance.arbitrage.corpus-runner-receipt/v0.1"
_RESEARCH_REPORT_SCHEMA = "resonance.arbitrage.corpus-research-report/v0.2"


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


def _clock_ms() -> int:
    return time.time_ns() // 1_000_000


def terminal_operation_count(corpus: RealMarketReplayCorpus) -> int:
    return len(
        {
            record.replay_case.logical_operation_id
            for record in corpus.records
            if record.replay_case.outcome.terminal
        }
    )


@dataclass(frozen=True, slots=True)
class CorpusRunnerConfig:
    horizon_ms: int = 60_000
    max_hops: int = 3
    max_cases: int = 20
    rolling_samples: int = 5
    rolling_interval_ms: int = 1_000
    rolling_horizon_ms: int = 5_000
    rolling_min_coverage_ratio: float = 0.8
    min_terminal_operations: int = 100
    min_training_rows: int = 20
    quality_policy: CorpusQualityPolicy = field(default_factory=CorpusQualityPolicy)
    benchmark_when_ready: bool = False

    def __post_init__(self) -> None:
        if self.horizon_ms < 1:
            raise ValueError("horizon_ms must be >= 1")
        if self.max_hops < 2:
            raise ValueError("max_hops must be >= 2")
        if self.max_cases < 1:
            raise ValueError("max_cases must be >= 1")
        if self.rolling_samples < 3:
            raise ValueError("rolling_samples must be >= 3")
        if self.rolling_interval_ms < 1:
            raise ValueError("rolling_interval_ms must be >= 1")
        if self.rolling_horizon_ms < 1:
            raise ValueError("rolling_horizon_ms must be >= 1")
        if not math.isfinite(self.rolling_min_coverage_ratio) or not (
            0.0 < self.rolling_min_coverage_ratio <= 1.0
        ):
            raise ValueError("rolling_min_coverage_ratio must be in (0, 1]")
        if self.min_terminal_operations < 1:
            raise ValueError("min_terminal_operations must be >= 1")
        if self.min_training_rows < 2:
            raise ValueError("min_training_rows must be >= 2")
        if not isinstance(self.quality_policy, CorpusQualityPolicy):
            raise ValueError("quality_policy must be CorpusQualityPolicy")

    @property
    def required_terminal_operations(self) -> int:
        # A walk-forward benchmark needs at least one validation row beyond training.
        return max(self.min_terminal_operations, self.min_training_rows + 1)


@dataclass(frozen=True, slots=True)
class CorpusResearchReport:
    status: str
    terminal_operation_count: int
    required_terminal_operations: int
    benchmark_requested: bool
    benchmark_executed: bool
    corpus_sha256: str
    replay_bundle_sha256: str
    quality_report_sha256: str
    quality_report_payload: Mapping[str, Any]
    comparison_sha256: str | None = None
    comparison_payload: Mapping[str, Any] | None = None
    reason: str | None = None
    paper_only: bool = True
    public_market_data_only: bool = True
    automatic_promotion: bool = False

    def __post_init__(self) -> None:
        allowed = {
            "NOT_READY",
            "READY",
            "BENCHMARK_COMPLETE",
            "BENCHMARK_UNAVAILABLE",
            "BENCHMARK_NOT_EVALUABLE",
        }
        if self.status not in allowed:
            raise ValueError("invalid research report status")
        if self.terminal_operation_count < 0:
            raise ValueError("terminal_operation_count cannot be negative")
        if self.required_terminal_operations < 1:
            raise ValueError("required_terminal_operations must be positive")
        if self.paper_only is not True or self.public_market_data_only is not True:
            raise ValueError("research report must remain public-data paper-only")
        if self.automatic_promotion is not False:
            raise ValueError("research report cannot enable automatic promotion")
        if not isinstance(self.quality_report_payload, Mapping):
            raise ValueError("research report requires corpus quality evidence")
        if _sha256(self.quality_report_payload) != self.quality_report_sha256:
            raise ValueError("corpus quality report SHA-256 does not match payload")
        if self.quality_report_payload.get("corpus_sha256") != self.corpus_sha256:
            raise ValueError("corpus quality report is bound to a different corpus")
        if self.status != "NOT_READY" and self.quality_report_payload.get("quality_ready") is not True:
            raise ValueError("research-ready status requires a passing corpus quality gate")
        if self.benchmark_executed:
            if self.status != "BENCHMARK_COMPLETE":
                raise ValueError("executed benchmark must have BENCHMARK_COMPLETE status")
            if not self.comparison_sha256 or self.comparison_payload is None:
                raise ValueError("executed benchmark must bind comparison evidence")
        elif self.comparison_sha256 is not None or self.comparison_payload is not None:
            raise ValueError("non-executed benchmark cannot carry comparison evidence")

    def to_payload(self) -> dict[str, Any]:
        return {
            "schema": _RESEARCH_REPORT_SCHEMA,
            "status": self.status,
            "terminal_operation_count": self.terminal_operation_count,
            "required_terminal_operations": self.required_terminal_operations,
            "benchmark_requested": self.benchmark_requested,
            "benchmark_executed": self.benchmark_executed,
            "corpus_sha256": self.corpus_sha256,
            "replay_bundle_sha256": self.replay_bundle_sha256,
            "quality_report_sha256": self.quality_report_sha256,
            "quality_report_payload": dict(self.quality_report_payload),
            "comparison_sha256": self.comparison_sha256,
            "comparison_payload": (
                dict(self.comparison_payload)
                if self.comparison_payload is not None
                else None
            ),
            "reason": self.reason,
            "paper_only": self.paper_only,
            "public_market_data_only": self.public_market_data_only,
            "automatic_promotion": self.automatic_promotion,
            "interpretation": "RESEARCH_DIAGNOSTIC_ONLY",
        }

    @property
    def sha256(self) -> str:
        return _sha256(self.to_payload())


BenchmarkFn = Callable[[ReplayBundle, int], tuple[Mapping[str, Any], str]]


def _default_benchmark(bundle: ReplayBundle, min_training_rows: int) -> tuple[Mapping[str, Any], str]:
    from .predictive import build_predictive_dataset
    from .predictive_catboost import CatBoostResearchConfig, run_catboost_walk_forward

    dataset = build_predictive_dataset(bundle)
    comparison = run_catboost_walk_forward(
        dataset,
        config=CatBoostResearchConfig(),
        min_training_rows=min_training_rows,
    )
    return comparison.to_payload(), comparison.sha256


def _quality_fields(report: CorpusQualityReport) -> dict[str, Any]:
    return {
        "quality_report_sha256": report.sha256,
        "quality_report_payload": report.to_payload(),
    }


def build_research_report(
    corpus: RealMarketReplayCorpus,
    *,
    config: CorpusRunnerConfig,
    benchmark_fn: BenchmarkFn | None = None,
) -> CorpusResearchReport:
    bundle = corpus.to_replay_bundle()
    terminal_count = terminal_operation_count(corpus)
    required = config.required_terminal_operations
    quality = build_corpus_quality_report(corpus, policy=config.quality_policy)
    quality_fields = _quality_fields(quality)

    readiness_failures: list[str] = []
    if terminal_count < required:
        readiness_failures.append(
            f"need {required - terminal_count} more terminal operations"
        )
    if not quality.quality_ready:
        readiness_failures.append(
            "quality gate failed: " + ", ".join(quality.failed_dimensions)
        )
    if readiness_failures:
        return CorpusResearchReport(
            status="NOT_READY",
            terminal_operation_count=terminal_count,
            required_terminal_operations=required,
            benchmark_requested=config.benchmark_when_ready,
            benchmark_executed=False,
            corpus_sha256=corpus.sha256,
            replay_bundle_sha256=bundle.sha256,
            reason="; ".join(readiness_failures),
            **quality_fields,
        )

    if not config.benchmark_when_ready:
        return CorpusResearchReport(
            status="READY",
            terminal_operation_count=terminal_count,
            required_terminal_operations=required,
            benchmark_requested=False,
            benchmark_executed=False,
            corpus_sha256=corpus.sha256,
            replay_bundle_sha256=bundle.sha256,
            reason="quantity and corpus-quality gates passed; benchmark was not requested",
            **quality_fields,
        )

    runner = benchmark_fn or _default_benchmark
    try:
        comparison_payload, comparison_sha256 = runner(
            bundle,
            config.min_training_rows,
        )
    except RuntimeError as exc:
        return CorpusResearchReport(
            status="BENCHMARK_UNAVAILABLE",
            terminal_operation_count=terminal_count,
            required_terminal_operations=required,
            benchmark_requested=True,
            benchmark_executed=False,
            corpus_sha256=corpus.sha256,
            replay_bundle_sha256=bundle.sha256,
            reason=str(exc),
            **quality_fields,
        )
    except ValueError as exc:
        return CorpusResearchReport(
            status="BENCHMARK_NOT_EVALUABLE",
            terminal_operation_count=terminal_count,
            required_terminal_operations=required,
            benchmark_requested=True,
            benchmark_executed=False,
            corpus_sha256=corpus.sha256,
            replay_bundle_sha256=bundle.sha256,
            reason=str(exc),
            **quality_fields,
        )

    expected_comparison_sha256 = _sha256(comparison_payload)
    if comparison_sha256 != expected_comparison_sha256:
        raise ValueError("benchmark comparison SHA-256 does not match payload")

    return CorpusResearchReport(
        status="BENCHMARK_COMPLETE",
        terminal_operation_count=terminal_count,
        required_terminal_operations=required,
        benchmark_requested=True,
        benchmark_executed=True,
        corpus_sha256=corpus.sha256,
        replay_bundle_sha256=bundle.sha256,
        comparison_sha256=comparison_sha256,
        comparison_payload=comparison_payload,
        **quality_fields,
    )


@dataclass(frozen=True, slots=True)
class CorpusRunReceipt:
    venue: str
    pairs: tuple[str, ...]
    horizon_ms: int
    decision_at_ms: int
    outcome_not_before_ms: int
    outcome_observed_at_ms: int
    pre_corpus_sha256: str
    decision_corpus_sha256: str
    post_corpus_sha256: str
    replay_bundle_sha256: str
    captured_operation_ids: tuple[str, ...]
    resolved_operation_ids: tuple[str, ...]
    research_report_sha256: str
    paper_only: bool = True
    public_market_data_only: bool = True

    def __post_init__(self) -> None:
        if not self.venue or not self.pairs:
            raise ValueError("runner receipt requires venue and pairs")
        if self.horizon_ms < 1:
            raise ValueError("runner receipt horizon must be positive")
        if self.outcome_not_before_ms != self.decision_at_ms + self.horizon_ms:
            raise ValueError("outcome_not_before_ms does not match decision horizon")
        if self.outcome_observed_at_ms < self.outcome_not_before_ms:
            raise ValueError("outcome was observed before configured horizon elapsed")
        if not self.captured_operation_ids:
            raise ValueError("runner receipt requires captured operations")
        if self.captured_operation_ids != self.resolved_operation_ids:
            raise ValueError("one-shot runner must resolve exactly its captured operations")
        if self.paper_only is not True or self.public_market_data_only is not True:
            raise ValueError("runner receipt must remain public-data paper-only")
        for name in (
            "pre_corpus_sha256",
            "decision_corpus_sha256",
            "post_corpus_sha256",
            "replay_bundle_sha256",
            "research_report_sha256",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or len(value) != 64:
                raise ValueError(f"{name} must be a SHA-256 digest")

    def to_payload(self) -> dict[str, Any]:
        return {
            "schema": _RUN_RECEIPT_SCHEMA,
            "venue": self.venue,
            "pairs": list(self.pairs),
            "horizon_ms": self.horizon_ms,
            "decision_at_ms": self.decision_at_ms,
            "outcome_not_before_ms": self.outcome_not_before_ms,
            "outcome_observed_at_ms": self.outcome_observed_at_ms,
            "pre_corpus_sha256": self.pre_corpus_sha256,
            "decision_corpus_sha256": self.decision_corpus_sha256,
            "post_corpus_sha256": self.post_corpus_sha256,
            "replay_bundle_sha256": self.replay_bundle_sha256,
            "captured_operation_ids": list(self.captured_operation_ids),
            "resolved_operation_ids": list(self.resolved_operation_ids),
            "research_report_sha256": self.research_report_sha256,
            "paper_only": self.paper_only,
            "public_market_data_only": self.public_market_data_only,
        }

    @property
    def sha256(self) -> str:
        return _sha256(self.to_payload())


@dataclass(frozen=True, slots=True)
class CorpusRunnerResult:
    receipt: CorpusRunReceipt
    research_report: CorpusResearchReport

    def to_envelope(self) -> dict[str, Any]:
        payload = {
            "receipt": self.receipt.to_payload(),
            "receipt_sha256": self.receipt.sha256,
            "research_report": self.research_report.to_payload(),
            "research_report_sha256": self.research_report.sha256,
        }
        return {
            "payload": payload,
            "sha256": _sha256(payload),
        }


CollectFn = Callable[..., tuple[list[QuoteSnapshot], dict[str, list[QuoteSnapshot]]]]
FetchFn = Callable[[Any, Sequence[tuple[str, str, str]]], list[QuoteSnapshot]]


def run_one_shot(
    *,
    corpus_path: str | Path,
    replay_output_path: str | Path,
    adapter: Any,
    pairs: Sequence[tuple[str, str, str]],
    start_asset: str,
    amount: float,
    costs: CostAssumption,
    config: CorpusRunnerConfig | None = None,
    engine_policy: Policy | None = None,
    regime_policy: RegimePolicy | None = None,
    regime_execution_policy: RegimeExecutionPolicy | None = None,
    clock_ms: Callable[[], int] = _clock_ms,
    sleep_fn: Callable[[float], None] = time.sleep,
    collect_fn: CollectFn = _collect_rolling_quotes,
    fetch_fn: FetchFn = _fetch_round,
    benchmark_fn: BenchmarkFn | None = None,
) -> CorpusRunnerResult:
    config = config or CorpusRunnerConfig()
    pairs = tuple(pairs)
    if not pairs:
        raise ValueError("runner requires at least one public market pair")
    if not start_asset:
        raise ValueError("start_asset must be non-empty")
    if not math.isfinite(amount) or amount <= 0:
        raise ValueError("amount must be finite and positive")

    corpus = load_corpus(corpus_path)
    pre_corpus_sha256 = corpus.sha256

    quotes, history = collect_fn(
        adapter,
        pairs,
        sample_count=config.rolling_samples,
        interval_ms=config.rolling_interval_ms,
        sleep_fn=sleep_fn,
    )
    decision_at_ms = clock_ms()
    window_policy = RollingWindowPolicy(
        horizon_ms=config.rolling_horizon_ms,
        min_samples=config.rolling_samples,
        min_coverage_ratio=config.rolling_min_coverage_ratio,
    )
    windows = {
        key: RollingMarketWindow.from_quotes(
            samples,
            policy=window_policy,
            end_ms=samples[-1].observed_at_ms,
        )
        for key, samples in history.items()
    }

    active_engine_policy = engine_policy or Policy()
    opportunities = scan_cycles(
        quotes,
        start=Node(adapter.venue, start_asset.upper()),
        amount=amount,
        costs_by_venue={adapter.venue: costs},
        now_ms=decision_at_ms,
        max_hops=config.max_hops,
        policy=active_engine_policy,
    )
    selected = tuple(opportunities[: config.max_cases])
    if not selected:
        raise ValueError("public scan produced no cycle candidates to record")

    decision_cases = build_decision_cases(
        quotes,
        windows,
        selected,
        costs_by_venue={adapter.venue: costs},
        evaluation_time_ms=decision_at_ms,
        start_amount=amount,
        engine_policy=active_engine_policy,
        regime_policy=regime_policy or RegimePolicy(),
        regime_execution_policy=(
            regime_execution_policy or RegimeExecutionPolicy()
        ),
        operation_prefix=f"real-market-{adapter.venue}",
    )
    captured_ids = tuple(case.logical_operation_id for case in decision_cases)
    corpus = corpus.append_decisions(decision_cases, captured_at_ms=decision_at_ms)
    save_corpus(corpus_path, corpus)
    decision_corpus_sha256 = corpus.sha256

    outcome_not_before_ms = decision_at_ms + config.horizon_ms
    sleep_fn(config.horizon_ms / 1000.0)
    after_sleep_ms = clock_ms()
    if after_sleep_ms < outcome_not_before_ms:
        raise ValueError(
            "configured outcome horizon has not elapsed; decision remains pending"
        )

    outcome_snapshots = tuple(fetch_fn(adapter, pairs))
    if not outcome_snapshots:
        raise ValueError("outcome capture returned no public quote snapshots")
    if any(
        snapshot.observed_at_ms < outcome_not_before_ms
        for snapshot in outcome_snapshots
    ):
        raise ValueError(
            "outcome quote was observed before configured horizon; decisions remain pending"
        )
    outcome_observed_at_ms = max(
        after_sleep_ms,
        *(snapshot.observed_at_ms for snapshot in outcome_snapshots),
    )

    # Resolve all newly captured decisions first; append only if the full batch is valid.
    terminal_cases = tuple(
        resolve_replay_case(
            case,
            outcome_snapshots,
            observed_at_ms=outcome_observed_at_ms,
        )
        for case in decision_cases
    )
    updated = corpus
    for terminal_case in terminal_cases:
        updated = updated.append_outcome(
            terminal_case,
            outcome_snapshots,
            captured_at_ms=outcome_observed_at_ms,
        )
    save_corpus(corpus_path, updated)

    # Reload from disk to verify the persisted envelope/hash chain before export/reporting.
    verified = load_corpus(corpus_path)
    if verified.sha256 != updated.sha256:
        raise ValueError("persisted corpus SHA-256 changed after verification reload")
    export_replay_bundle(replay_output_path, verified)
    replay_bundle = verified.to_replay_bundle()

    research_report = build_research_report(
        verified,
        config=config,
        benchmark_fn=benchmark_fn,
    )
    resolved_ids = tuple(case.logical_operation_id for case in terminal_cases)
    receipt = CorpusRunReceipt(
        venue=adapter.venue,
        pairs=tuple(f"{symbol}:{base}:{quote}" for symbol, base, quote in pairs),
        horizon_ms=config.horizon_ms,
        decision_at_ms=decision_at_ms,
        outcome_not_before_ms=outcome_not_before_ms,
        outcome_observed_at_ms=outcome_observed_at_ms,
        pre_corpus_sha256=pre_corpus_sha256,
        decision_corpus_sha256=decision_corpus_sha256,
        post_corpus_sha256=verified.sha256,
        replay_bundle_sha256=replay_bundle.sha256,
        captured_operation_ids=captured_ids,
        resolved_operation_ids=resolved_ids,
        research_report_sha256=research_report.sha256,
    )
    return CorpusRunnerResult(receipt=receipt, research_report=research_report)


def save_runner_result(path: str | Path, result: CorpusRunnerResult) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(result.to_envelope(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
