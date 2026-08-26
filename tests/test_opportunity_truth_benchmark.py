from __future__ import annotations

from copy import deepcopy
import hashlib
import json

import pytest

from resonance_arbitrage_graph.corpus_quality import CorpusQualityPolicy
from resonance_arbitrage_graph.opportunity_truth_benchmark import (
    BenchmarkClaimPolicy,
    BenchmarkClaimStatus,
    BenchmarkSourceKind,
    build_opportunity_truth_benchmark,
    render_opportunity_truth_benchmark_markdown,
    verify_opportunity_truth_benchmark_envelope,
    verify_opportunity_truth_benchmark_source_binding,
)
from resonance_arbitrage_graph.real_market_corpus import (
    RealMarketReplayCorpus,
    resolve_replay_case,
)
from test_real_market_corpus import (
    _decision_case,
    _outcome_quotes,
)
from test_walk_forward import _bundle


def _canonical_sha(payload: dict) -> str:
    raw = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _quality_policy() -> CorpusQualityPolicy:
    return CorpusQualityPolicy(
        min_decision_batches=1,
        min_effective_decision_batches=1.0,
        min_temporal_span_ms=0,
        min_distinct_routes=1,
        min_effective_routes=1.0,
        min_distinct_route_markets=3,
        min_distinct_regimes=1,
    )


def _real_corpus() -> RealMarketReplayCorpus:
    decision = _decision_case()
    corpus = RealMarketReplayCorpus().append_decisions(
        (decision,),
        captured_at_ms=decision.evaluation_time_ms,
    )
    terminal = resolve_replay_case(
        decision,
        _outcome_quotes(),
        observed_at_ms=2_000,
    )
    return corpus.append_outcome(
        terminal,
        _outcome_quotes(),
        captured_at_ms=2_000,
    )


def test_real_market_benchmark_is_deterministic_and_source_bound():
    corpus = _real_corpus()
    report = build_opportunity_truth_benchmark(
        corpus,
        claim_policy=BenchmarkClaimPolicy(
            min_terminal_operations=1,
            min_truth_events=1,
        ),
        quality_policy=_quality_policy(),
    )
    repeated = build_opportunity_truth_benchmark(
        corpus,
        claim_policy=report.claim_policy,
        quality_policy=_quality_policy(),
    )

    assert report.source_kind is BenchmarkSourceKind.REAL_MARKET_CORPUS
    assert report.claim_status is BenchmarkClaimStatus.INTERNAL_EVIDENCE_READY
    assert report.overall.funnel.candidate_opportunities == 1
    assert report.overall.funnel.truth_events == 1
    assert report.paper_pnl_by_start_state
    assert report.sha256 == repeated.sha256
    assert report.canonical_payload() == repeated.canonical_payload()
    assert verify_opportunity_truth_benchmark_envelope(report.to_envelope())
    assert verify_opportunity_truth_benchmark_source_binding(report, corpus)


def test_small_real_corpus_does_not_create_a_marketing_claim():
    report = build_opportunity_truth_benchmark(
        _real_corpus(),
        quality_policy=_quality_policy(),
    )

    assert report.claim_status is BenchmarkClaimStatus.NOT_READY
    assert "terminal_operations" in report.claim_reasons
    assert "truth_events" in report.claim_reasons


def test_replay_bundle_is_measurable_but_not_real_market_claim_ready():
    bundle = _bundle()
    report = build_opportunity_truth_benchmark(
        bundle,
        claim_policy=BenchmarkClaimPolicy(
            min_terminal_operations=1,
            min_truth_events=1,
            require_corpus_quality=False,
        ),
    )

    assert report.source_kind is BenchmarkSourceKind.REPLAY_BUNDLE
    assert report.claim_status is BenchmarkClaimStatus.UNASSESSED_REPLAY_SOURCE
    assert report.corpus_quality_payload is None
    assert verify_opportunity_truth_benchmark_source_binding(report, bundle)


def test_tampered_truth_rate_is_rejected_even_with_recomputed_outer_sha():
    report = build_opportunity_truth_benchmark(
        _real_corpus(),
        claim_policy=BenchmarkClaimPolicy(
            min_terminal_operations=1,
            min_truth_events=1,
        ),
        quality_policy=_quality_policy(),
    )
    envelope = deepcopy(report.to_envelope())
    envelope["payload"]["overall"]["opportunity_truth_rate"] = 0.123
    envelope["sha256"] = _canonical_sha(envelope["payload"])

    with pytest.raises(ValueError, match="opportunity_truth_rate"):
        verify_opportunity_truth_benchmark_envelope(envelope)


def test_source_binding_rejects_different_bundle():
    report = build_opportunity_truth_benchmark(_bundle())
    other = _real_corpus().to_replay_bundle()

    with pytest.raises(ValueError, match="does not reproduce"):
        verify_opportunity_truth_benchmark_source_binding(report, other)


def test_markdown_keeps_product_claim_boundary_visible():
    report = build_opportunity_truth_benchmark(
        _real_corpus(),
        quality_policy=_quality_policy(),
    )
    rendered = render_opportunity_truth_benchmark_markdown(report)

    assert "Opportunity Truth Benchmark" in rendered
    assert "Claim status" in rendered
    assert "paper" in rendered.lower()
    assert "not a live-fill" in rendered
