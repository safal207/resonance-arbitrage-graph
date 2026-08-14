from __future__ import annotations

from dataclasses import replace

import pytest

from resonance_arbitrage_graph.corpus_quality import (
    CorpusQualityPolicy,
    build_corpus_quality_report,
)
from resonance_arbitrage_graph.engine import Policy
from resonance_arbitrage_graph.model import Node
from resonance_arbitrage_graph.quotes import CostAssumption, QuoteSnapshot
from resonance_arbitrage_graph.real_market_corpus import (
    RealMarketReplayCorpus,
    RealMarketReplayRecord,
    build_decision_cases,
)
from resonance_arbitrage_graph.regime import RegimePolicy
from resonance_arbitrage_graph.regime_gate import RegimeExecutionPolicy
from resonance_arbitrage_graph.replay import ReplayOutcome
from resonance_arbitrage_graph.rolling_state import (
    RollingMarketWindow,
    RollingWindowPolicy,
)
from resonance_arbitrage_graph.scanner import scan_cycles
from resonance_arbitrage_graph.window_regime import market_key


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
        venue="fixture",
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


def _quotes(at_ms: int) -> tuple[QuoteSnapshot, ...]:
    return (
        _quote("BTCUSDT", "BTC", "USDT", bid=99.9, ask=100.0, observed_at_ms=at_ms),
        _quote("ETHBTC", "ETH", "BTC", bid=0.0499, ask=0.05, observed_at_ms=at_ms),
        _quote("ETHUSDT", "ETH", "USDT", bid=5.09, ask=5.10, observed_at_ms=at_ms),
    )


def _windows(at_ms: int) -> dict[str, RollingMarketWindow]:
    policy = RollingWindowPolicy(
        horizon_ms=250,
        min_samples=3,
        min_coverage_ratio=0.5,
    )
    history: dict[str, list[QuoteSnapshot]] = {}
    for sample_at, multiplier in (
        (at_ms - 200, 0.999),
        (at_ms - 100, 1.0),
        (at_ms, 1.001),
    ):
        for quote in _quotes(sample_at):
            adjusted = replace(
                quote,
                bid_price=quote.bid_price * multiplier,
                ask_price=quote.ask_price * multiplier,
            )
            history.setdefault(
                market_key(adjusted.venue, adjusted.symbol), []
            ).append(adjusted)
    return {
        key: RollingMarketWindow.from_quotes(
            rows,
            policy=policy,
            end_ms=at_ms,
        )
        for key, rows in history.items()
    }


def _regime_policy(*, volatile: bool = False) -> RegimePolicy:
    return RegimePolicy(
        volatile_return_bps=0.0 if volatile else 1_000_000.0,
        thin_capacity_ratio=0.0,
        dislocated_cross_rate_bps=1_000_000.0,
        wide_spread_bps=1_000_000.0,
    )


def _decision(
    at_ms: int,
    *,
    operation_prefix: str,
    start_asset: str = "USDT",
    volatile: bool = False,
):
    quotes = _quotes(at_ms)
    costs = CostAssumption(fee_bps=0.0, slippage_bps=0.0)
    opportunities = scan_cycles(
        quotes,
        start=Node("fixture", start_asset),
        amount=1_000.0,
        costs_by_venue={"fixture": costs},
        now_ms=at_ms,
        max_hops=3,
        policy=Policy(),
    )
    triangle = next(item for item in opportunities if len(item.route) == 3)
    return build_decision_cases(
        quotes,
        _windows(at_ms),
        (triangle,),
        costs_by_venue={"fixture": costs},
        evaluation_time_ms=at_ms,
        start_amount=1_000.0,
        engine_policy=Policy(),
        regime_policy=_regime_policy(volatile=volatile),
        regime_execution_policy=RegimeExecutionPolicy(),
        operation_prefix=operation_prefix,
    )[0]


def _clone(decision, suffix: str):
    operation_id = f"{decision.logical_operation_id}-{suffix}"
    return replace(
        decision,
        logical_operation_id=operation_id,
        case_id=f"{operation_id}:attempt:1",
    )


def _terminal(decision):
    return replace(
        decision,
        case_id=f"{decision.logical_operation_id}:attempt:2",
        attempt=2,
        outcome=ReplayOutcome(
            observed_at_ms=decision.evaluation_time_ms + 1_000,
            expired=True,
        ),
    )


def _corpus(decisions) -> RealMarketReplayCorpus:
    records: list[RealMarketReplayRecord] = []
    previous_sha: str | None = None
    for decision in decisions:
        decision_record = RealMarketReplayRecord(
            sequence=len(records) + 1,
            previous_record_sha256=previous_sha,
            phase="DECISION",
            captured_at_ms=decision.evaluation_time_ms,
            replay_case=decision,
        )
        records.append(decision_record)
        previous_sha = decision_record.sha256

        terminal = _terminal(decision)
        outcome_record = RealMarketReplayRecord(
            sequence=len(records) + 1,
            previous_record_sha256=previous_sha,
            phase="OUTCOME",
            captured_at_ms=terminal.outcome.observed_at_ms,
            replay_case=terminal,
        )
        records.append(outcome_record)
        previous_sha = outcome_record.sha256
    return RealMarketReplayCorpus(records=tuple(records))


def _policy(**overrides) -> CorpusQualityPolicy:
    values = {
        "min_decision_batches": 1,
        "min_effective_decision_batches": 1.0,
        "min_temporal_span_ms": 0,
        "min_distinct_routes": 1,
        "min_effective_routes": 1.0,
        "min_distinct_route_markets": 3,
        "min_distinct_regimes": 1,
    }
    values.update(overrides)
    return CorpusQualityPolicy(**values)


def test_many_operations_from_few_market_moments_do_not_fake_readiness():
    first = _decision(1_000, operation_prefix="batch-a")
    second = _decision(2_000, operation_prefix="batch-b")
    decisions = [
        *(_clone(first, f"a-{index}") for index in range(5)),
        *(_clone(second, f"b-{index}") for index in range(5)),
    ]
    corpus = _corpus(decisions)
    policy = _policy(
        min_decision_batches=5,
        min_effective_decision_batches=4.0,
    )

    report = build_corpus_quality_report(corpus, policy=policy)
    repeated = build_corpus_quality_report(corpus, policy=policy)

    assert report.terminal_operation_count == 10
    assert report.distinct_decision_batches == 2
    assert report.effective_decision_batches == pytest.approx(2.0)
    assert "decision_batches" in report.failed_dimensions
    assert "effective_decision_batches" in report.failed_dimensions
    assert report.quality_ready is False
    assert repeated.sha256 == report.sha256
    assert repeated.to_payload() == report.to_payload()


def test_effective_batch_count_detects_one_dominant_market_moment():
    dominant = _decision(1_000, operation_prefix="dominant")
    decisions = [_clone(dominant, f"dominant-{index}") for index in range(20)]
    for index in range(1, 10):
        decisions.append(
            _decision(
                1_000 + index * 1_000,
                operation_prefix=f"minor-{index}",
            )
        )
    report = build_corpus_quality_report(
        _corpus(decisions),
        policy=_policy(
            min_decision_batches=10,
            min_effective_decision_batches=5.0,
        ),
    )

    assert report.distinct_decision_batches == 10
    assert report.effective_decision_batches < 5.0
    assert report.largest_decision_batch_share == pytest.approx(20 / 29)
    assert "decision_batches" not in report.failed_dimensions
    assert "effective_decision_batches" in report.failed_dimensions


def test_effective_route_count_detects_route_topology_concentration():
    usdt = _decision(1_000, operation_prefix="route-usdt", start_asset="USDT")
    btc = _decision(2_000, operation_prefix="route-btc", start_asset="BTC")
    eth = _decision(3_000, operation_prefix="route-eth", start_asset="ETH")
    decisions = [_clone(usdt, f"main-{index}") for index in range(18)] + [btc, eth]

    report = build_corpus_quality_report(
        _corpus(decisions),
        policy=_policy(
            min_distinct_routes=3,
            min_effective_routes=2.0,
        ),
    )

    assert report.distinct_routes == 3
    assert report.effective_routes < 2.0
    assert report.largest_route_share == pytest.approx(18 / 20)
    assert "distinct_routes" not in report.failed_dimensions
    assert "effective_routes" in report.failed_dimensions


def test_market_and_regime_diversity_are_derived_from_decision_evidence():
    normal = _decision(1_000, operation_prefix="normal", volatile=False)
    volatile = _decision(2_000, operation_prefix="volatile", volatile=True)
    corpus = _corpus((normal, volatile))

    report = build_corpus_quality_report(
        corpus,
        policy=_policy(
            min_decision_batches=2,
            min_effective_decision_batches=2.0,
            min_distinct_route_markets=4,
            min_distinct_regimes=2,
        ),
    )

    assert report.distinct_route_markets == 3
    assert report.distinct_regimes == 2
    assert {name for name, _count in report.regime_counts} == {"NORMAL", "VOLATILE"}
    assert "distinct_route_markets" in report.failed_dimensions
    assert "distinct_regimes" not in report.failed_dimensions
