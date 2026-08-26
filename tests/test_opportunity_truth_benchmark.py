from copy import deepcopy
from dataclasses import replace

import pytest

from resonance_arbitrage_graph.opportunity_truth_benchmark import (
    OpportunityTruthBenchmarkStatus,
    OpportunityTruthEvidenceSource,
    build_opportunity_truth_benchmark,
    build_opportunity_truth_benchmark_from_corpus,
    render_opportunity_truth_markdown,
    verify_opportunity_truth_benchmark_envelope,
)
from resonance_arbitrage_graph.real_market_corpus import RealMarketReplayCorpus
from resonance_arbitrage_graph.replay import ReplayOutcome
from test_walk_forward import _bundle, _case


def _real_market_corpus() -> RealMarketReplayCorpus:
    terminal_fixture = _case(
        "product-real-market",
        1,
        volatility="low",
        edge_bps=32.0,
        realized_edge_bps=32.0,
    )
    decision = replace(
        terminal_fixture,
        outcome=ReplayOutcome(observed_at_ms=terminal_fixture.evaluation_time_ms),
    )
    corpus = RealMarketReplayCorpus().append_decisions(
        (decision,),
        captured_at_ms=decision.evaluation_time_ms,
    )
    expired = replace(
        decision,
        case_id=f"{decision.logical_operation_id}-a2",
        attempt=2,
        outcome=ReplayOutcome(
            observed_at_ms=decision.evaluation_time_ms + 1_000,
            expired=True,
        ),
    )
    return corpus.append_outcome(
        expired,
        (),
        captured_at_ms=expired.outcome.observed_at_ms,
    )


def test_benchmark_is_deterministic_and_reproducible():
    bundle = _bundle()
    first = build_opportunity_truth_benchmark(bundle, min_truth_population=1)
    second = build_opportunity_truth_benchmark(bundle, min_truth_population=1)

    assert first.sha256 == second.sha256
    assert first.canonical_payload() == second.canonical_payload()
    assert first.candidate_opportunities == len(bundle.collapsed_cases())
    assert (
        first.execute_sim_decisions + first.observe_decisions + first.reject_decisions
        == first.candidate_opportunities
    )
    assert first.evidence_source is OpportunityTruthEvidenceSource.REPLAY_BUNDLE
    assert first.source_corpus_sha256 is None
    assert not first.public_claim_eligible
    assert verify_opportunity_truth_benchmark_envelope(
        first.to_envelope(),
        source=bundle,
    )


def test_sample_size_gate_prevents_premature_product_claim():
    report = build_opportunity_truth_benchmark(_bundle(), min_truth_population=10_000)
    assert report.status is OpportunityTruthBenchmarkStatus.INSUFFICIENT_TRUTH_POPULATION
    assert not report.sample_size_gate_passed
    assert not report.public_claim_eligible

    rendered = render_opportunity_truth_markdown(report)
    assert "NOT READY" in rendered
    assert "Public claims require evidence_source=REAL_MARKET_CORPUS" in rendered


def test_real_market_builder_binds_corpus_identity():
    corpus = _real_market_corpus()
    report = build_opportunity_truth_benchmark_from_corpus(
        corpus,
        min_truth_population=1,
    )

    assert report.evidence_source is OpportunityTruthEvidenceSource.REAL_MARKET_CORPUS
    assert report.source_corpus_sha256 == corpus.sha256
    assert report.public_claim_eligible is report.sample_size_gate_passed
    assert verify_opportunity_truth_benchmark_envelope(
        report.to_envelope(),
        source=corpus,
    )

    with pytest.raises(ValueError, match="does not reproduce"):
        verify_opportunity_truth_benchmark_envelope(
            report.to_envelope(),
            source=corpus.to_replay_bundle(),
        )


def test_benchmark_exposes_truth_and_paper_pnl_metrics():
    report = build_opportunity_truth_benchmark(_bundle(), min_truth_population=1)
    assert report.truth_population == (
        report.metrics.true_positive + report.metrics.false_positive
    )
    assert report.evaluated_execute_sim_capital >= 0
    if report.evaluated_execute_sim_capital:
        assert report.realized_paper_return_bps is not None


def test_report_tamper_is_rejected_even_with_original_outer_digest():
    bundle = _bundle()
    report = build_opportunity_truth_benchmark(bundle, min_truth_population=1)
    envelope = deepcopy(report.to_envelope())
    envelope["payload"]["candidate_opportunities"] += 1
    with pytest.raises(ValueError, match="SHA-256"):
        verify_opportunity_truth_benchmark_envelope(envelope, source=bundle)


def test_min_truth_population_rejects_bool():
    with pytest.raises(ValueError, match="integer"):
        build_opportunity_truth_benchmark(_bundle(), min_truth_population=True)
