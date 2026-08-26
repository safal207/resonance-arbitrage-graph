from __future__ import annotations

from copy import deepcopy
from dataclasses import replace
import hashlib
import json

import pytest

from resonance_arbitrage_graph.corpus_quality import CorpusQualityPolicy
from resonance_arbitrage_graph.opportunity_truth_benchmark_v2 import (
    OpportunityTruthClaimPolicy,
    OpportunityTruthClaimStatus,
    build_opportunity_truth_benchmark_v2,
    render_opportunity_truth_benchmark_v2_markdown,
    verify_opportunity_truth_benchmark_v2_envelope,
    verify_opportunity_truth_benchmark_v2_source_binding,
)
from resonance_arbitrage_graph.real_market_corpus import (
    RealMarketReplayCorpus,
    resolve_replay_case,
    save_corpus,
)
from resonance_arbitrage_graph.replay import ReplayBundle, ReplayOutcome
from test_corpus_quality import _decision
from test_real_market_corpus import _decision_case, _outcome_quotes
from test_walk_forward import _bundle, _case


def _canonical_sha(payload: dict) -> str:
    raw = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _permissive_quality() -> CorpusQualityPolicy:
    return CorpusQualityPolicy(
        min_decision_batches=1,
        min_effective_decision_batches=1.0,
        min_temporal_span_ms=0,
        min_distinct_routes=1,
        min_effective_routes=1.0,
        min_distinct_route_markets=3,
        min_distinct_regimes=1,
    )


def _clone(decision, suffix: str):
    operation_id = f"{decision.logical_operation_id}-{suffix}"
    return replace(
        decision,
        logical_operation_id=operation_id,
        case_id=f"{operation_id}:attempt:1",
    )


def _real_corpus(count: int = 1) -> RealMarketReplayCorpus:
    base = _decision_case()
    decisions = tuple(_clone(base, str(index)) for index in range(count))
    corpus = RealMarketReplayCorpus().append_decisions(
        decisions,
        captured_at_ms=base.evaluation_time_ms,
    )
    for decision in decisions:
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
    return corpus


def test_v2_is_deterministic_quality_bound_and_source_reproducible():
    corpus = _real_corpus()
    policy = OpportunityTruthClaimPolicy(
        min_terminal_operations=1,
        min_truth_events=1,
    )
    first = build_opportunity_truth_benchmark_v2(
        corpus,
        claim_policy=policy,
        quality_policy=_permissive_quality(),
    )
    second = build_opportunity_truth_benchmark_v2(
        corpus,
        claim_policy=policy,
        quality_policy=_permissive_quality(),
    )

    assert (
        first.claim_status
        is OpportunityTruthClaimStatus.INTERNAL_EVIDENCE_READY
    )
    assert first.internal_evidence_ready is True
    assert first.corpus_quality["quality_ready"] is True
    assert first.truth_population == 1
    assert first.truth_coverage is not None
    assert first.paper_pnl_by_start_state
    assert first.sha256 == second.sha256
    assert first.canonical_payload() == second.canonical_payload()
    assert verify_opportunity_truth_benchmark_v2_envelope(
        first.to_envelope()
    )
    assert verify_opportunity_truth_benchmark_v2_source_binding(
        first, corpus
    )


def test_sample_and_terminal_gates_can_pass_while_quality_still_blocks_readiness():
    corpus = _real_corpus()
    report = build_opportunity_truth_benchmark_v2(
        corpus,
        claim_policy=OpportunityTruthClaimPolicy(
            min_terminal_operations=1,
            min_truth_events=1,
        ),
    )

    assert report.terminal_operations >= 1
    assert report.truth_population >= 1
    assert report.claim_status is OpportunityTruthClaimStatus.NOT_READY
    assert report.internal_evidence_ready is False
    assert report.corpus_quality["quality_ready"] is False
    assert any(
        reason.startswith("corpus_quality:")
        for reason in report.claim_reasons
    )


def test_replay_fixture_is_measurable_but_unassessed_for_claim_readiness():
    report = build_opportunity_truth_benchmark_v2(
        _bundle(),
        claim_policy=OpportunityTruthClaimPolicy(
            min_terminal_operations=1,
            min_truth_events=1,
            require_corpus_quality=False,
        ),
    )

    assert (
        report.claim_status
        is OpportunityTruthClaimStatus.UNASSESSED_REPLAY_SOURCE
    )
    assert report.internal_evidence_ready is False
    assert report.corpus_quality is None
    assert report.claim_reasons == ("real_market_corpus_provenance",)


def test_mixed_start_assets_are_never_summed_into_one_pnl_total():
    usdt = _case(
        "mixed-usdt",
        1,
        volatility="low",
        edge_bps=32.0,
        realized_edge_bps=32.0,
    )
    btc_decision = _decision(
        500_000,
        operation_prefix="mixed-btc",
        start_asset="BTC",
    )
    btc = replace(
        btc_decision,
        outcome=ReplayOutcome(
            observed_at_ms=btc_decision.evaluation_time_ms + 1_000,
            realized_net_edge_bps=20.0,
        ),
    )
    report = build_opportunity_truth_benchmark_v2(
        ReplayBundle(cases=(usdt, btc)),
        claim_policy=OpportunityTruthClaimPolicy(
            min_terminal_operations=1,
            min_truth_events=1,
            require_corpus_quality=False,
        ),
    )

    states = {row.start_state for row in report.paper_pnl_by_start_state}
    assert states == {"fixture:BTC", "fixture:USDT"}
    assert all(
        row.capital_units > 0
        for row in report.paper_pnl_by_start_state
    )
    assert (
        report.canonical_payload()["legacy_cross_unit_pnl_is_not_used"]
        is True
    )


def test_tampered_edge_decay_is_rejected_even_with_recomputed_outer_sha():
    report = build_opportunity_truth_benchmark_v2(
        _real_corpus(),
        claim_policy=OpportunityTruthClaimPolicy(1, 1),
        quality_policy=_permissive_quality(),
    )
    envelope = deepcopy(report.to_envelope())
    envelope["payload"]["mean_edge_decay_bps"] += 1.0
    envelope["sha256"] = _canonical_sha(envelope["payload"])

    with pytest.raises(ValueError, match="edge decay"):
        verify_opportunity_truth_benchmark_v2_envelope(envelope)


def test_full_binding_rejects_a_different_source():
    report = build_opportunity_truth_benchmark_v2(_bundle())
    other = _real_corpus().to_replay_bundle()

    with pytest.raises(ValueError, match="does not reproduce"):
        verify_opportunity_truth_benchmark_v2_source_binding(
            report, other
        )


def test_markdown_states_internal_not_publication_boundary():
    report = build_opportunity_truth_benchmark_v2(
        _real_corpus(),
        claim_policy=OpportunityTruthClaimPolicy(1, 1),
        quality_policy=_permissive_quality(),
    )
    rendered = render_opportunity_truth_benchmark_v2_markdown(report)

    assert "INTERNAL_EVIDENCE_READY" in rendered
    assert "not publication approval" in rendered
    assert "exact starting state" in rendered


def test_cli_build_and_verify_v2(tmp_path):
    from resonance_arbitrage_graph.opportunity_truth_benchmark_cli import main

    corpus_path = tmp_path / "corpus.json"
    report_path = tmp_path / "benchmark-v2.json"
    markdown_path = tmp_path / "benchmark-v2.md"
    save_corpus(corpus_path, _real_corpus())

    assert main(
        [
            "build",
            str(corpus_path),
            "--min-terminal-operations",
            "1",
            "--min-truth-population",
            "1",
            "--min-decision-batches",
            "1",
            "--min-effective-decision-batches",
            "1",
            "--min-temporal-span-ms",
            "0",
            "--min-distinct-routes",
            "1",
            "--min-effective-routes",
            "1",
            "--min-distinct-route-markets",
            "3",
            "--min-distinct-regimes",
            "1",
            "--output",
            str(report_path),
            "--markdown-output",
            str(markdown_path),
        ]
    ) == 0
    assert main(["verify", str(corpus_path), str(report_path)]) == 0
    assert main(["render", str(report_path)]) == 0
    assert "Opportunity Truth Benchmark v0.2" in markdown_path.read_text(
        encoding="utf-8"
    )
