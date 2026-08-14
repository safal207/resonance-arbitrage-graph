from __future__ import annotations

import hashlib
import json

import pytest

from resonance_arbitrage_graph.corpus_runner import (
    CorpusRunnerConfig,
    run_one_shot,
    terminal_operation_count,
)
from resonance_arbitrage_graph.quotes import CostAssumption, QuoteSnapshot
from resonance_arbitrage_graph.real_market_corpus import load_corpus
from resonance_arbitrage_graph.window_regime import market_key


PAIRS = (
    ("BTCUSDT", "BTC", "USDT"),
    ("ETHBTC", "ETH", "BTC"),
    ("ETHUSDT", "ETH", "USDT"),
)


class FakeAdapter:
    venue = "binance"


class FakeClock:
    def __init__(self, now_ms: int = 10_000):
        self.now_ms = now_ms

    def __call__(self) -> int:
        return self.now_ms

    def sleep(self, seconds: float) -> None:
        self.now_ms += int(round(seconds * 1_000.0))


def _quote(
    symbol: str,
    base: str,
    quote: str,
    *,
    bid: float,
    ask: float,
    observed_at_ms: int,
) -> QuoteSnapshot:
    return QuoteSnapshot(
        venue="binance",
        symbol=symbol,
        base_asset=base,
        quote_asset=quote,
        bid_price=bid,
        bid_qty=10_000.0,
        ask_price=ask,
        ask_qty=10_000.0,
        observed_at_ms=observed_at_ms,
        source_url=f"https://public.example/{symbol}",
    )


def _market_round(observed_at_ms: int, *, outcome: bool = False) -> list[QuoteSnapshot]:
    # USDT -> BTC -> ETH -> USDT is deliberately profitable in the paper model.
    eth_usdt_bid = 56.0 if outcome else 60.0
    eth_usdt_ask = eth_usdt_bid + 1.0
    return [
        _quote(
            "BTCUSDT",
            "BTC",
            "USDT",
            bid=99.0,
            ask=100.0,
            observed_at_ms=observed_at_ms,
        ),
        _quote(
            "ETHBTC",
            "ETH",
            "BTC",
            bid=0.49,
            ask=0.50,
            observed_at_ms=observed_at_ms,
        ),
        _quote(
            "ETHUSDT",
            "ETH",
            "USDT",
            bid=eth_usdt_bid,
            ask=eth_usdt_ask,
            observed_at_ms=observed_at_ms,
        ),
    ]


def _collector(clock: FakeClock):
    def collect(_adapter, _pairs, *, sample_count, interval_ms, sleep_fn):
        del interval_ms, sleep_fn
        step_ms = 500
        first_ms = clock.now_ms - step_ms * (sample_count - 1)
        history: dict[str, list[QuoteSnapshot]] = {}
        latest: list[QuoteSnapshot] = []
        for index in range(sample_count):
            observed_at_ms = first_ms + index * step_ms
            latest = _market_round(observed_at_ms)
            for snapshot in latest:
                history.setdefault(
                    market_key(snapshot.venue, snapshot.symbol), []
                ).append(snapshot)
        return latest, history

    return collect


def _fetcher(clock: FakeClock):
    def fetch(_adapter, _pairs):
        return _market_round(clock.now_ms, outcome=True)

    return fetch


def _config(**overrides) -> CorpusRunnerConfig:
    values = {
        "horizon_ms": 1_000,
        "max_hops": 3,
        "max_cases": 1,
        "rolling_samples": 3,
        "rolling_interval_ms": 1,
        "rolling_horizon_ms": 1_000,
        "rolling_min_coverage_ratio": 1.0,
        "min_terminal_operations": 100,
        "min_training_rows": 20,
        "benchmark_when_ready": False,
    }
    values.update(overrides)
    return CorpusRunnerConfig(**values)


def _run(tmp_path, clock: FakeClock, *, config=None, sleep_fn=None, benchmark_fn=None):
    return run_one_shot(
        corpus_path=tmp_path / "corpus.json",
        replay_output_path=tmp_path / "replay.json",
        adapter=FakeAdapter(),
        pairs=PAIRS,
        start_asset="USDT",
        amount=1_000.0,
        costs=CostAssumption(fee_bps=0.0, slippage_bps=0.0),
        config=config or _config(),
        clock_ms=clock,
        sleep_fn=sleep_fn or clock.sleep,
        collect_fn=_collector(clock),
        fetch_fn=_fetcher(clock),
        benchmark_fn=benchmark_fn,
    )


def _digest(payload) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def test_one_shot_appends_terminal_pair_and_reports_not_ready(tmp_path):
    clock = FakeClock()
    result = _run(tmp_path, clock)

    corpus = load_corpus(tmp_path / "corpus.json")
    assert len(corpus.records) == 2
    assert not corpus.pending_cases()
    assert terminal_operation_count(corpus) == 1
    assert (tmp_path / "replay.json").exists()

    assert result.research_report.status == "NOT_READY"
    assert result.research_report.terminal_operation_count == 1
    assert result.research_report.required_terminal_operations == 100
    assert result.receipt.captured_operation_ids == result.receipt.resolved_operation_ids
    assert result.receipt.outcome_observed_at_ms >= result.receipt.outcome_not_before_ms
    assert result.receipt.post_corpus_sha256 == corpus.sha256
    assert result.receipt.replay_bundle_sha256 == corpus.to_replay_bundle().sha256


def test_horizon_failure_leaves_decision_pending_without_fake_outcome(tmp_path):
    clock = FakeClock()

    with pytest.raises(ValueError, match="horizon has not elapsed"):
        _run(tmp_path, clock, sleep_fn=lambda _seconds: None)

    corpus = load_corpus(tmp_path / "corpus.json")
    assert len(corpus.records) == 1
    assert len(corpus.pending_cases()) == 1
    assert terminal_operation_count(corpus) == 0
    assert not (tmp_path / "replay.json").exists()


def test_benchmark_is_never_called_below_research_threshold(tmp_path):
    clock = FakeClock()
    calls = []

    def benchmark(_bundle, _min_training_rows):
        calls.append(True)
        raise AssertionError("benchmark must not run below readiness threshold")

    result = _run(
        tmp_path,
        clock,
        config=_config(
            min_terminal_operations=3,
            min_training_rows=2,
            benchmark_when_ready=True,
        ),
        benchmark_fn=benchmark,
    )

    assert result.research_report.status == "NOT_READY"
    assert result.research_report.benchmark_requested is True
    assert result.research_report.benchmark_executed is False
    assert calls == []


def test_ready_corpus_runs_bound_benchmark_only_after_threshold(tmp_path):
    clock = FakeClock()
    calls = []

    def benchmark(bundle, min_training_rows):
        calls.append((bundle.sha256, min_training_rows))
        payload = {
            "schema": "test.comparison/v0.1",
            "folds": 1,
            "paper_only": True,
        }
        return payload, _digest(payload)

    config = _config(
        min_terminal_operations=3,
        min_training_rows=2,
        benchmark_when_ready=True,
    )

    first = _run(tmp_path, clock, config=config, benchmark_fn=benchmark)
    second = _run(tmp_path, clock, config=config, benchmark_fn=benchmark)
    third = _run(tmp_path, clock, config=config, benchmark_fn=benchmark)

    assert first.research_report.status == "NOT_READY"
    assert second.research_report.status == "NOT_READY"
    assert third.research_report.status == "BENCHMARK_COMPLETE"
    assert third.research_report.benchmark_executed is True
    assert len(calls) == 1
    assert third.research_report.comparison_sha256 == _digest(
        third.research_report.comparison_payload
    )
    assert terminal_operation_count(load_corpus(tmp_path / "corpus.json")) == 3


def test_new_one_shot_does_not_resolve_an_old_pending_operation(tmp_path):
    clock = FakeClock()

    with pytest.raises(ValueError, match="horizon has not elapsed"):
        _run(tmp_path, clock, sleep_fn=lambda _seconds: None)

    old_pending_id = load_corpus(tmp_path / "corpus.json").pending_cases()[0].logical_operation_id
    clock.now_ms = 12_000
    result = _run(tmp_path, clock)

    corpus = load_corpus(tmp_path / "corpus.json")
    pending_ids = {case.logical_operation_id for case in corpus.pending_cases()}
    assert old_pending_id in pending_ids
    assert old_pending_id not in result.receipt.resolved_operation_ids
    assert terminal_operation_count(corpus) == 1


def test_outcome_snapshot_before_horizon_is_rejected_and_decision_stays_pending(tmp_path):
    clock = FakeClock()

    def stale_fetch(_adapter, _pairs):
        return _market_round(clock.now_ms - 1, outcome=True)

    with pytest.raises(ValueError, match="observed before configured horizon"):
        run_one_shot(
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
            fetch_fn=stale_fetch,
        )

    corpus = load_corpus(tmp_path / "corpus.json")
    assert len(corpus.pending_cases()) == 1
    assert terminal_operation_count(corpus) == 0
