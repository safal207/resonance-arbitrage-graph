from __future__ import annotations

import hashlib
import json

import pytest

from resonance_arbitrage_graph.corpus_campaign import (
    recover_matured_pending_cases,
    run_resumable_campaign_step,
)
from resonance_arbitrage_graph.quotes import CostAssumption
from resonance_arbitrage_graph.real_market_corpus import load_corpus
from test_corpus_runner import (
    FakeAdapter,
    FakeClock,
    PAIRS,
    _collector,
    _config,
    _fetcher,
    _market_round,
    _run,
)


def _digest(payload) -> str:
    return hashlib.sha256(
        json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
    ).hexdigest()


def test_resumable_step_recovers_old_pending_before_new_capture(tmp_path):
    clock = FakeClock()

    with pytest.raises(ValueError, match="horizon has not elapsed"):
        _run(tmp_path, clock, sleep_fn=lambda _seconds: None)

    old_pending = load_corpus(tmp_path / "corpus.json").pending_cases()
    assert len(old_pending) == 1
    old_id = old_pending[0].logical_operation_id

    clock.now_ms = 12_000
    result = run_resumable_campaign_step(
        corpus_path=tmp_path / "corpus.json",
        replay_output_path=tmp_path / "replay.json",
        adapter=FakeAdapter(),
        pairs=PAIRS,
        start_asset="USDT",
        amount=1_000.0,
        costs=CostAssumption(fee_bps=0.0, slippage_bps=0.0),
        config=_config(),
        clock_ms=clock,
        sleep_fn=clock.sleep,
        collect_fn=_collector(clock),
        fetch_fn=_fetcher(clock),
    )

    corpus = load_corpus(tmp_path / "corpus.json")
    assert not corpus.pending_cases()
    assert len(corpus.to_replay_bundle().collapsed_cases()) == 2
    assert result.recovery.recovered_operation_ids == (old_id,)
    assert old_id not in result.one_shot.receipt.resolved_operation_ids
    assert result.recovery.pre_corpus_sha256 != result.recovery.post_corpus_sha256

    envelope = result.to_envelope()
    assert envelope["sha256"] == _digest(envelope["payload"])


def test_recovery_ignores_pending_from_different_market_set(tmp_path):
    clock = FakeClock()
    with pytest.raises(ValueError, match="horizon has not elapsed"):
        _run(tmp_path, clock, sleep_fn=lambda _seconds: None)

    clock.now_ms = 12_000
    other_pairs = (
        ("BTCUSDT", "BTC", "USDT"),
        ("SOLBTC", "SOL", "BTC"),
        ("SOLUSDT", "SOL", "USDT"),
    )
    calls = []

    def forbidden_fetch(_adapter, _pairs):
        calls.append(True)
        raise AssertionError("different market set must not be fetched")

    receipt = recover_matured_pending_cases(
        corpus_path=tmp_path / "corpus.json",
        adapter=FakeAdapter(),
        pairs=other_pairs,
        horizon_ms=1_000,
        clock_ms=clock,
        fetch_fn=forbidden_fetch,
    )

    assert receipt.recovered_operation_ids == ()
    assert receipt.observed_at_ms is None
    assert calls == []
    assert len(load_corpus(tmp_path / "corpus.json").pending_cases()) == 1


def test_recovery_rejects_outcome_before_horizon_without_rewriting_pending(tmp_path):
    clock = FakeClock()
    with pytest.raises(ValueError, match="horizon has not elapsed"):
        _run(tmp_path, clock, sleep_fn=lambda _seconds: None)

    clock.now_ms = 12_000

    def stale_fetch(_adapter, _pairs):
        return _market_round(10_999, outcome=True)

    with pytest.raises(ValueError, match="predates configured horizon"):
        recover_matured_pending_cases(
            corpus_path=tmp_path / "corpus.json",
            adapter=FakeAdapter(),
            pairs=PAIRS,
            horizon_ms=1_000,
            clock_ms=clock,
            fetch_fn=stale_fetch,
        )

    corpus = load_corpus(tmp_path / "corpus.json")
    assert len(corpus.pending_cases()) == 1
    assert len(corpus.records) == 1
