from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
import hashlib
import hmac
import json
from pathlib import Path
import time
from typing import Any

from .corpus_runner import (
    BenchmarkFn,
    CollectFn,
    CorpusRunnerConfig,
    CorpusRunnerResult,
    FetchFn,
    run_one_shot,
)
from .engine import Policy
from .live_scan import _collect_rolling_quotes, _fetch_round
from .quotes import CostAssumption, QuoteSnapshot
from .real_market_corpus import (
    load_corpus,
    resolve_replay_case,
    save_corpus,
)
from .regime import RegimePolicy
from .regime_gate import RegimeExecutionPolicy


_STEP_SCHEMA = "resonance.verify.corpus-campaign-step/v0.1"
_RECOVERY_SCHEMA = "resonance.verify.corpus-pending-recovery/v0.1"


def _json(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def _sha(value: Any) -> str:
    return hashlib.sha256(_json(value).encode("utf-8")).hexdigest()


def _market_set_from_pairs(
    pairs: Sequence[tuple[str, str, str]],
) -> tuple[tuple[str, str], ...]:
    values = tuple(
        sorted(
            {
                (base.strip().upper(), quote.strip().upper())
                for symbol, base, quote in pairs
                if symbol and base and quote
            }
        )
    )
    if not values:
        raise ValueError("campaign recovery requires public market pairs")
    return values


def _market_set_from_case(case) -> tuple[tuple[str, str], ...]:
    return tuple(
        sorted(
            {
                (snapshot.base_asset, snapshot.quote_asset)
                for snapshot in case.snapshots
            }
        )
    )


@dataclass(frozen=True, slots=True)
class PendingRecoveryReceipt:
    venue: str
    horizon_ms: int
    market_set: tuple[tuple[str, str], ...]
    observed_at_ms: int | None
    pre_corpus_sha256: str
    post_corpus_sha256: str
    recovered_operation_ids: tuple[str, ...]
    paper_only: bool = True
    public_market_data_only: bool = True

    def __post_init__(self) -> None:
        object.__setattr__(self, "market_set", tuple(self.market_set))
        object.__setattr__(
            self,
            "recovered_operation_ids",
            tuple(sorted(set(self.recovered_operation_ids))),
        )
        if not self.venue:
            raise ValueError("recovery receipt venue must be non-empty")
        if self.horizon_ms < 1:
            raise ValueError("recovery horizon must be positive")
        if not self.market_set:
            raise ValueError("recovery market set must be non-empty")
        if self.observed_at_ms is not None and self.observed_at_ms < 0:
            raise ValueError("recovery observed_at_ms cannot be negative")
        for name in ("pre_corpus_sha256", "post_corpus_sha256"):
            value = getattr(self, name)
            if not isinstance(value, str) or len(value) != 64:
                raise ValueError(f"{name} must be a SHA-256 digest")
        if not self.recovered_operation_ids:
            if self.observed_at_ms is not None:
                raise ValueError(
                    "empty recovery cannot claim an outcome observation"
                )
            if self.pre_corpus_sha256 != self.post_corpus_sha256:
                raise ValueError("empty recovery cannot change corpus identity")
        elif self.observed_at_ms is None:
            raise ValueError("recovered operations require observation time")
        if self.paper_only is not True or self.public_market_data_only is not True:
            raise ValueError("recovery must remain public-data paper-only")

    def canonical_payload(self) -> dict[str, Any]:
        return {
            "schema": _RECOVERY_SCHEMA,
            "venue": self.venue,
            "horizon_ms": self.horizon_ms,
            "market_set": [
                {"base_asset": base, "quote_asset": quote}
                for base, quote in self.market_set
            ],
            "observed_at_ms": self.observed_at_ms,
            "pre_corpus_sha256": self.pre_corpus_sha256,
            "post_corpus_sha256": self.post_corpus_sha256,
            "recovered_operation_ids": list(self.recovered_operation_ids),
            "paper_only": self.paper_only,
            "public_market_data_only": self.public_market_data_only,
        }

    @property
    def sha256(self) -> str:
        return _sha(self.canonical_payload())


@dataclass(frozen=True, slots=True)
class CorpusCampaignStepResult:
    recovery: PendingRecoveryReceipt
    one_shot: CorpusRunnerResult

    def to_envelope(self) -> dict[str, Any]:
        run_envelope = self.one_shot.to_envelope()
        payload = {
            "schema": _STEP_SCHEMA,
            "recovery": self.recovery.canonical_payload(),
            "recovery_sha256": self.recovery.sha256,
            "one_shot": run_envelope,
            "paper_only": True,
            "public_market_data_only": True,
        }
        return {"payload": payload, "sha256": _sha(payload)}


def recover_matured_pending_cases(
    *,
    corpus_path: str | Path,
    adapter: Any,
    pairs: Sequence[tuple[str, str, str]],
    horizon_ms: int,
    clock_ms: Callable[[], int],
    fetch_fn: FetchFn,
) -> PendingRecoveryReceipt:
    if horizon_ms < 1:
        raise ValueError("horizon_ms must be positive")
    pair_tuple = tuple(pairs)
    market_set = _market_set_from_pairs(pair_tuple)
    corpus = load_corpus(corpus_path)
    pre_sha = corpus.sha256
    now_ms = clock_ms()

    matured = tuple(
        case
        for case in corpus.pending_cases()
        if {snapshot.venue for snapshot in case.snapshots} == {adapter.venue}
        and _market_set_from_case(case) == market_set
        and now_ms >= case.evaluation_time_ms + horizon_ms
    )
    if not matured:
        return PendingRecoveryReceipt(
            venue=adapter.venue,
            horizon_ms=horizon_ms,
            market_set=market_set,
            observed_at_ms=None,
            pre_corpus_sha256=pre_sha,
            post_corpus_sha256=pre_sha,
            recovered_operation_ids=(),
        )

    due_ms = max(case.evaluation_time_ms + horizon_ms for case in matured)
    outcome_snapshots = tuple(fetch_fn(adapter, pair_tuple))
    if not outcome_snapshots:
        raise ValueError("pending recovery returned no public quote snapshots")
    if {
        (snapshot.base_asset, snapshot.quote_asset)
        for snapshot in outcome_snapshots
    } != set(market_set):
        raise ValueError("pending recovery returned a different public market set")
    if any(snapshot.observed_at_ms < due_ms for snapshot in outcome_snapshots):
        raise ValueError("pending recovery quote predates configured horizon")

    observed_at_ms = max(
        clock_ms(),
        *(snapshot.observed_at_ms for snapshot in outcome_snapshots),
    )
    terminal_cases = tuple(
        resolve_replay_case(
            case,
            outcome_snapshots,
            observed_at_ms=observed_at_ms,
        )
        for case in matured
    )
    updated = corpus
    for terminal_case in terminal_cases:
        updated = updated.append_outcome(
            terminal_case,
            outcome_snapshots,
            captured_at_ms=observed_at_ms,
        )
    save_corpus(corpus_path, updated)
    verified = load_corpus(corpus_path)
    if not hmac.compare_digest(verified.sha256, updated.sha256):
        raise ValueError("pending recovery changed after persisted reload")

    return PendingRecoveryReceipt(
        venue=adapter.venue,
        horizon_ms=horizon_ms,
        market_set=market_set,
        observed_at_ms=observed_at_ms,
        pre_corpus_sha256=pre_sha,
        post_corpus_sha256=verified.sha256,
        recovered_operation_ids=tuple(
            case.logical_operation_id for case in terminal_cases
        ),
    )


def run_resumable_campaign_step(
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
    clock_ms: Callable[[], int] = lambda: time.time_ns() // 1_000_000,
    sleep_fn: Callable[[float], None] = time.sleep,
    collect_fn: CollectFn = _collect_rolling_quotes,
    fetch_fn: FetchFn = _fetch_round,
    benchmark_fn: BenchmarkFn | None = None,
) -> CorpusCampaignStepResult:
    active_config = config or CorpusRunnerConfig()
    recovery = recover_matured_pending_cases(
        corpus_path=corpus_path,
        adapter=adapter,
        pairs=pairs,
        horizon_ms=active_config.horizon_ms,
        clock_ms=clock_ms,
        fetch_fn=fetch_fn,
    )
    result = run_one_shot(
        corpus_path=corpus_path,
        replay_output_path=replay_output_path,
        adapter=adapter,
        pairs=pairs,
        start_asset=start_asset,
        amount=amount,
        costs=costs,
        config=active_config,
        engine_policy=engine_policy,
        regime_policy=regime_policy,
        regime_execution_policy=regime_execution_policy,
        clock_ms=clock_ms,
        sleep_fn=sleep_fn,
        collect_fn=collect_fn,
        fetch_fn=fetch_fn,
        benchmark_fn=benchmark_fn,
    )
    return CorpusCampaignStepResult(recovery=recovery, one_shot=result)
