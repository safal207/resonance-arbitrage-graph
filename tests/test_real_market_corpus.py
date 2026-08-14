from __future__ import annotations

from dataclasses import replace

import pytest

from resonance_arbitrage_graph.engine import Policy
from resonance_arbitrage_graph.model import Node
from resonance_arbitrage_graph.quotes import CostAssumption, QuoteSnapshot
from resonance_arbitrage_graph.real_market_corpus import (
    RealMarketReplayCorpus,
    RealMarketReplayRecord,
    build_decision_cases,
    realized_future_edge_bps,
    resolve_replay_case,
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


def _decision_quotes(at_ms: int = 1_000) -> tuple[QuoteSnapshot, ...]:
    return (
        _quote("BTCUSDT", "BTC", "USDT", 99.9, 100.0, at_ms),
        _quote("ETHBTC", "ETH", "BTC", 0.0499, 0.05, at_ms),
        _quote("ETHUSDT", "ETH", "USDT", 5.09, 5.10, at_ms),
    )


def _outcome_quotes(at_ms: int = 2_000) -> tuple[QuoteSnapshot, ...]:
    return (
        _quote("BTCUSDT", "BTC", "USDT", 99.8, 100.1, at_ms),
        _quote("ETHBTC", "ETH", "BTC", 0.0500, 0.0501, at_ms),
        _quote("ETHUSDT", "ETH", "USDT", 4.80, 4.81, at_ms),
    )


def _windows() -> dict[str, RollingMarketWindow]:
    policy = RollingWindowPolicy(
        horizon_ms=250,
        min_samples=3,
        min_coverage_ratio=0.5,
    )
    history: dict[str, list[QuoteSnapshot]] = {}
    for at_ms, multiplier in ((800, 0.999), (900, 1.0), (1_000, 1.001)):
        for quote in _decision_quotes(at_ms):
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
            end_ms=1_000,
        )
        for key, rows in history.items()
    }


def _decision_case():
    quotes = _decision_quotes()
    costs = CostAssumption(fee_bps=0.0, slippage_bps=0.0)
    opportunities = scan_cycles(
        quotes,
        start=Node("fixture", "USDT"),
        amount=1_000.0,
        costs_by_venue={"fixture": costs},
        now_ms=1_000,
        max_hops=3,
        policy=Policy(),
    )
    triangle = next(item for item in opportunities if len(item.route) == 3)
    return build_decision_cases(
        quotes,
        _windows(),
        (triangle,),
        costs_by_venue={"fixture": costs},
        evaluation_time_ms=1_000,
        start_amount=1_000.0,
        engine_policy=Policy(),
        regime_policy=RegimePolicy(),
        regime_execution_policy=RegimeExecutionPolicy(),
        operation_prefix="test-real-market",
    )[0]


def test_real_market_corpus_appends_decision_then_verifiable_outcome():
    decision = _decision_case()
    corpus = RealMarketReplayCorpus().append_decisions(
        (decision,),
        captured_at_ms=1_000,
    )
    assert corpus.pending_cases() == (decision,)

    terminal = resolve_replay_case(
        decision,
        _outcome_quotes(),
        observed_at_ms=2_000,
    )
    corpus = corpus.append_outcome(
        terminal,
        _outcome_quotes(),
        captured_at_ms=2_000,
    )

    assert corpus.pending_cases() == ()
    bundle = corpus.to_replay_bundle()
    collapsed = bundle.collapsed_cases()
    assert len(collapsed) == 1
    assert collapsed[0].attempt == 2
    assert collapsed[0].outcome.terminal is True
    assert collapsed[0].outcome.realized_net_edge_bps == pytest.approx(
        realized_future_edge_bps(
            decision,
            _outcome_quotes(),
            observed_at_ms=2_000,
        )
    )


def test_corpus_hash_chain_rejects_record_rewrite():
    decision = _decision_case()
    corpus = RealMarketReplayCorpus().append_decisions(
        (decision,),
        captured_at_ms=1_000,
    )
    terminal = resolve_replay_case(
        decision,
        _outcome_quotes(),
        observed_at_ms=2_000,
    )
    corpus = corpus.append_outcome(
        terminal,
        _outcome_quotes(),
        captured_at_ms=2_000,
    )

    tampered = replace(
        corpus.records[1],
        previous_record_sha256="0" * 64,
    )
    with pytest.raises(ValueError, match="hash chain"):
        RealMarketReplayCorpus(records=(corpus.records[0], tampered))


def test_outcome_record_rejects_realized_edge_not_supported_by_public_quotes():
    decision = _decision_case()
    terminal = resolve_replay_case(
        decision,
        _outcome_quotes(),
        observed_at_ms=2_000,
    )
    assert terminal.outcome.realized_net_edge_bps is not None
    tampered_case = replace(
        terminal,
        outcome=ReplayOutcome(
            observed_at_ms=2_000,
            realized_net_edge_bps=terminal.outcome.realized_net_edge_bps + 1.0,
        ),
    )
    with pytest.raises(ValueError, match="does not match outcome snapshots"):
        RealMarketReplayRecord(
            sequence=2,
            previous_record_sha256="a" * 64,
            phase="OUTCOME",
            captured_at_ms=2_000,
            replay_case=tampered_case,
            outcome_snapshots=_outcome_quotes(),
        )


def test_corpus_envelope_round_trip_preserves_identity():
    decision = _decision_case()
    corpus = RealMarketReplayCorpus().append_decisions(
        (decision,),
        captured_at_ms=1_000,
    )
    rebuilt = RealMarketReplayCorpus.from_envelope(corpus.to_envelope())

    assert rebuilt.sha256 == corpus.sha256
    assert rebuilt.canonical_payload() == corpus.canonical_payload()


def test_resolution_fails_when_future_public_quote_set_misses_route_market():
    decision = _decision_case()
    with pytest.raises(ValueError, match="exactly one fresh quote"):
        resolve_replay_case(
            decision,
            _outcome_quotes()[:2],
            observed_at_ms=2_000,
        )
