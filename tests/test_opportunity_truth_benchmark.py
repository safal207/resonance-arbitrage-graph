from copy import deepcopy

import pytest

from resonance_arbitrage_graph.opportunity_truth_benchmark import (
    OpportunityTruthBenchmarkStatus,
    build_opportunity_truth_benchmark,
    render_opportunity_truth_markdown,
    verify_opportunity_truth_benchmark_envelope,
)
from test_walk_forward import _bundle


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
    assert verify_opportunity_truth_benchmark_envelope(
        first.to_envelope(),
        bundle=bundle,
    )


def test_sample_size_gate_prevents_premature_product_claim():
    report = build_opportunity_truth_benchmark(_bundle(), min_truth_population=10_000)
    assert report.status is OpportunityTruthBenchmarkStatus.INSUFFICIENT_TRUTH_POPULATION
    assert not report.sample_size_gate_passed

    rendered = render_opportunity_truth_markdown(report)
    assert "NOT READY" in rendered
    assert "Public marketing claims must be generated from a captured real-market corpus" in rendered


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
        verify_opportunity_truth_benchmark_envelope(envelope, bundle=bundle)


def test_min_truth_population_rejects_bool():
    with pytest.raises(ValueError, match="integer"):
        build_opportunity_truth_benchmark(_bundle(), min_truth_population=True)
