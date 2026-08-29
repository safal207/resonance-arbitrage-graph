from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
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
from .quotes import CostAssumption
from .real_market_corpus import (
    load_corpus,
    resolve_replay_case,
    save_corpus,
)
from .regime import RegimePolicy
from .regime_gate import RegimeExecutionPolicy


_STEP_SCHEMA = "resonance.verify.corpus-campaign-step/v0.1"
_RECOVERY_SCHEMA = "resonance.verify.corpus-pending-recovery/v0.1"
_POLICY_SCHEMA = "resonance.verify.corpus-campaign-policy/v0.1"


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


def _sha_text(value: Any, name: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise ValueError(f"{name} must be a lowercase SHA-256 digest")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{name} must be hexadecimal") from exc
    if value.lower() != value:
        raise ValueError(f"{name} must be lowercase")
    return value


def _text(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be non-empty")
    return value.strip()


def _market_set_from_pairs(
    pairs: Sequence[tuple[str, str, str]],
) -> tuple[tuple[str, str], ...]:
    pair_tuple = tuple(pairs)
    if not pair_tuple:
        raise ValueError("campaign recovery requires public market pairs")
    values: set[tuple[str, str]] = set()
    for item in pair_tuple:
        if not isinstance(item, tuple) or len(item) != 3:
            raise ValueError("campaign pair must be (symbol, base, quote)")
        symbol, base, quote = item
        _text(symbol, "pair symbol")
        normalized_base = _text(base, "pair base").upper()
        normalized_quote = _text(quote, "pair quote").upper()
        values.add((normalized_base, normalized_quote))
    return tuple(sorted(values))


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
class CorpusCampaignPolicy:
    campaign_id: str
    venue: str
    horizon_ms: int
    paper_only: bool = True
    public_market_data_only: bool = True

    def __post_init__(self) -> None:
        object.__setattr__(self, "campaign_id", _text(self.campaign_id, "campaign_id"))
        object.__setattr__(self, "venue", _text(self.venue, "venue"))
        if isinstance(self.horizon_ms, bool) or not isinstance(self.horizon_ms, int) or self.horizon_ms < 1:
            raise ValueError("campaign horizon_ms must be an integer >= 1")
        if self.paper_only is not True or self.public_market_data_only is not True:
            raise ValueError("campaign policy must remain public-data paper-only")

    def canonical_payload(self) -> dict[str, Any]:
        return {
            "schema": _POLICY_SCHEMA,
            "campaign_id": self.campaign_id,
            "venue": self.venue,
            "horizon_ms": self.horizon_ms,
            "dedicated_corpus_required": True,
            "paper_only": self.paper_only,
            "public_market_data_only": self.public_market_data_only,
        }

    @property
    def sha256(self) -> str:
        return _sha(self.canonical_payload())

    def to_envelope(self) -> dict[str, Any]:
        return {"payload": self.canonical_payload(), "sha256": self.sha256}

    @classmethod
    def from_envelope(cls, envelope: Mapping[str, Any]) -> "CorpusCampaignPolicy":
        if not isinstance(envelope, Mapping) or set(envelope) != {"payload", "sha256"}:
            raise ValueError("campaign policy envelope is not canonical")
        payload = envelope["payload"]
        if not isinstance(payload, Mapping):
            raise ValueError("campaign policy payload must be an object")
        keys = {
            "schema",
            "campaign_id",
            "venue",
            "horizon_ms",
            "dedicated_corpus_required",
            "paper_only",
            "public_market_data_only",
        }
        if set(payload) != keys or payload.get("schema") != _POLICY_SCHEMA:
            raise ValueError("unsupported campaign policy payload")
        if payload.get("dedicated_corpus_required") is not True:
            raise ValueError("campaign policy must require a dedicated corpus")
        policy = cls(
            campaign_id=payload["campaign_id"],
            venue=payload["venue"],
            horizon_ms=payload["horizon_ms"],
            paper_only=payload["paper_only"],
            public_market_data_only=payload["public_market_data_only"],
        )
        supplied = _sha_text(envelope["sha256"], "campaign_policy_sha256")
        if policy.canonical_payload() != dict(payload):
            raise ValueError("campaign policy payload is not canonical after reconstruction")
        if not hmac.compare_digest(policy.sha256, supplied):
            raise ValueError("campaign policy SHA-256 does not match payload")
        return policy


def campaign_policy_path(corpus_path: str | Path) -> Path:
    source = Path(corpus_path)
    return source.with_name(f"{source.stem}.campaign-policy.json")


def ensure_campaign_policy(
    corpus_path: str | Path,
    policy: CorpusCampaignPolicy,
) -> CorpusCampaignPolicy:
    if not isinstance(policy, CorpusCampaignPolicy):
        raise ValueError("policy must be CorpusCampaignPolicy")
    destination = campaign_policy_path(corpus_path)
    if destination.exists():
        raw = json.loads(destination.read_text(encoding="utf-8"))
        stored = CorpusCampaignPolicy.from_envelope(raw)
        if stored != policy:
            raise ValueError("campaign policy differs from the dedicated corpus manifest")
        return stored

    corpus = load_corpus(corpus_path)
    if corpus.records:
        raise ValueError(
            "cannot adopt a non-empty corpus without its original campaign policy"
        )
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(destination.name + ".tmp")
    temporary.write_text(
        json.dumps(policy.to_envelope(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(destination)
    stored = CorpusCampaignPolicy.from_envelope(
        json.loads(destination.read_text(encoding="utf-8"))
    )
    if stored != policy:
        raise ValueError("persisted campaign policy changed after reload")
    return stored


@dataclass(frozen=True, slots=True)
class PendingRecoveryReceipt:
    campaign_policy_sha256: str
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
        _sha_text(self.campaign_policy_sha256, "campaign_policy_sha256")
        object.__setattr__(self, "venue", _text(self.venue, "venue"))
        market_set = tuple(self.market_set)
        object.__setattr__(self, "market_set", market_set)
        if market_set != tuple(sorted(set(market_set))):
            raise ValueError("recovery market set must be sorted and unique")
        for base, quote in market_set:
            if (
                _text(base, "market base") != base.upper()
                or _text(quote, "market quote") != quote.upper()
            ):
                raise ValueError("recovery market assets must be canonical uppercase")
        recovered = tuple(self.recovered_operation_ids)
        object.__setattr__(self, "recovered_operation_ids", recovered)
        if recovered != tuple(sorted(set(recovered))):
            raise ValueError("recovered operation IDs must be sorted and unique")
        if any(not isinstance(item, str) or not item for item in recovered):
            raise ValueError("recovered operation IDs must be non-empty strings")
        if isinstance(self.horizon_ms, bool) or not isinstance(self.horizon_ms, int) or self.horizon_ms < 1:
            raise ValueError("recovery horizon must be an integer >= 1")
        if not self.market_set:
            raise ValueError("recovery market set must be non-empty")
        if self.observed_at_ms is not None and self.observed_at_ms < 0:
            raise ValueError("recovery observed_at_ms cannot be negative")
        _sha_text(self.pre_corpus_sha256, "pre_corpus_sha256")
        _sha_text(self.post_corpus_sha256, "post_corpus_sha256")
        if not recovered:
            if self.observed_at_ms is not None:
                raise ValueError("empty recovery cannot claim an outcome observation")
            if self.pre_corpus_sha256 != self.post_corpus_sha256:
                raise ValueError("empty recovery cannot change corpus identity")
        elif self.observed_at_ms is None:
            raise ValueError("recovered operations require observation time")
        if self.paper_only is not True or self.public_market_data_only is not True:
            raise ValueError("recovery must remain public-data paper-only")

    def canonical_payload(self) -> dict[str, Any]:
        return {
            "schema": _RECOVERY_SCHEMA,
            "campaign_policy_sha256": self.campaign_policy_sha256,
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
    campaign_policy: CorpusCampaignPolicy
    recovery: PendingRecoveryReceipt
    one_shot: CorpusRunnerResult

    def __post_init__(self) -> None:
        if not isinstance(self.campaign_policy, CorpusCampaignPolicy):
            raise ValueError("campaign_policy has invalid type")
        if not isinstance(self.recovery, PendingRecoveryReceipt):
            raise ValueError("recovery has invalid type")
        if not isinstance(self.one_shot, CorpusRunnerResult):
            raise ValueError("one_shot has invalid type")
        if not hmac.compare_digest(
            self.campaign_policy.sha256,
            self.recovery.campaign_policy_sha256,
        ):
            raise ValueError("recovery does not bind the campaign policy")
        if not hmac.compare_digest(
            self.recovery.post_corpus_sha256,
            self.one_shot.receipt.pre_corpus_sha256,
        ):
            raise ValueError("campaign recovery does not chain into one-shot input")

    def to_envelope(self) -> dict[str, Any]:
        run_envelope = self.one_shot.to_envelope()
        payload = {
            "schema": _STEP_SCHEMA,
            "campaign_policy": self.campaign_policy.canonical_payload(),
            "campaign_policy_sha256": self.campaign_policy.sha256,
            "recovery": self.recovery.canonical_payload(),
            "recovery_sha256": self.recovery.sha256,
            "one_shot": run_envelope,
            "paper_only": True,
            "public_market_data_only": True,
        }
        return {"payload": payload, "sha256": _sha(payload)}


def _recover_matured_pending_cases(
    *,
    corpus_path: str | Path,
    policy: CorpusCampaignPolicy,
    adapter: Any,
    pairs: Sequence[tuple[str, str, str]],
    clock_ms: Callable[[], int],
    fetch_fn: FetchFn,
) -> PendingRecoveryReceipt:
    pair_tuple = tuple(pairs)
    market_set = _market_set_from_pairs(pair_tuple)
    corpus = load_corpus(corpus_path)
    pre_sha = corpus.sha256
    now_ms = clock_ms()

    matured = tuple(
        case
        for case in corpus.pending_cases()
        if {snapshot.venue for snapshot in case.snapshots} == {policy.venue}
        and _market_set_from_case(case) == market_set
        and now_ms >= case.evaluation_time_ms + policy.horizon_ms
    )
    if not matured:
        return PendingRecoveryReceipt(
            campaign_policy_sha256=policy.sha256,
            venue=policy.venue,
            horizon_ms=policy.horizon_ms,
            market_set=market_set,
            observed_at_ms=None,
            pre_corpus_sha256=pre_sha,
            post_corpus_sha256=pre_sha,
            recovered_operation_ids=(),
        )

    due_ms = max(case.evaluation_time_ms + policy.horizon_ms for case in matured)
    outcome_snapshots = tuple(fetch_fn(adapter, pair_tuple))
    if not outcome_snapshots:
        raise ValueError("pending recovery returned no public quote snapshots")
    if {snapshot.venue for snapshot in outcome_snapshots} != {policy.venue}:
        raise ValueError("pending recovery returned a different venue")
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
        campaign_policy_sha256=policy.sha256,
        venue=policy.venue,
        horizon_ms=policy.horizon_ms,
        market_set=market_set,
        observed_at_ms=observed_at_ms,
        pre_corpus_sha256=pre_sha,
        post_corpus_sha256=verified.sha256,
        recovered_operation_ids=tuple(
            sorted(case.logical_operation_id for case in terminal_cases)
        ),
    )


def recover_matured_pending_cases(
    *,
    corpus_path: str | Path,
    adapter: Any,
    pairs: Sequence[tuple[str, str, str]],
    horizon_ms: int,
    clock_ms: Callable[[], int],
    fetch_fn: FetchFn,
    campaign_id: str = "corpus-campaign-001",
) -> PendingRecoveryReceipt:
    policy = ensure_campaign_policy(
        corpus_path,
        CorpusCampaignPolicy(campaign_id, adapter.venue, horizon_ms),
    )
    return _recover_matured_pending_cases(
        corpus_path=corpus_path,
        policy=policy,
        adapter=adapter,
        pairs=pairs,
        clock_ms=clock_ms,
        fetch_fn=fetch_fn,
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
    campaign_id: str = "corpus-campaign-001",
    clock_ms: Callable[[], int] = lambda: time.time_ns() // 1_000_000,
    sleep_fn: Callable[[float], None] = time.sleep,
    collect_fn: CollectFn = _collect_rolling_quotes,
    fetch_fn: FetchFn = _fetch_round,
    benchmark_fn: BenchmarkFn | None = None,
) -> CorpusCampaignStepResult:
    active_config = config or CorpusRunnerConfig()
    policy = ensure_campaign_policy(
        corpus_path,
        CorpusCampaignPolicy(campaign_id, adapter.venue, active_config.horizon_ms),
    )
    recovery = _recover_matured_pending_cases(
        corpus_path=corpus_path,
        policy=policy,
        adapter=adapter,
        pairs=pairs,
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
    return CorpusCampaignStepResult(
        campaign_policy=policy,
        recovery=recovery,
        one_shot=result,
    )
