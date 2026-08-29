from copy import deepcopy
from dataclasses import replace
import hashlib
import json

import pytest

from resonance_arbitrage_graph.opportunity_funnel import (
    build_opportunity_funnel,
    render_opportunity_funnel_markdown,
    verify_opportunity_funnel_envelope,
)
from resonance_arbitrage_graph.opportunity_funnel_cli import main as funnel_main
from resonance_arbitrage_graph.quotes import CostAssumption
from resonance_arbitrage_graph.real_market_corpus import save_corpus
from resonance_arbitrage_graph.replay import ReplayBundle
from test_opportunity_truth_benchmark_v2 import _real_corpus
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


def test_funnel_is_deterministic_and_fully_reproducible_from_real_corpus():
    corpus = _real_corpus()
    first = build_opportunity_funnel(corpus)
    second = build_opportunity_funnel(corpus)

    assert first.sha256 == second.sha256
    assert first.canonical_payload() == second.canonical_payload()
    assert first.overall.counts.candidate_cycles == 1
    assert first.overall.counts.complete_evidence == 1
    assert first.overall.counts.final_execute_sim == 1
    assert first.overall.counts.truth_outcomes == 1
    assert first.overall.counts.survived_required_edge == 1
    assert verify_opportunity_funnel_envelope(
        first.to_envelope(),
        source=corpus,
    )


def test_funnel_stages_are_cumulative_across_replay_population():
    report = build_opportunity_funnel(_bundle())
    counts = report.overall.counts
    values = (
        counts.candidate_cycles,
        counts.complete_evidence,
        counts.structural_constraints_pass,
        counts.gross_positive,
        counts.net_positive,
        counts.execute_threshold_eligible,
        counts.final_execute_sim,
        counts.resolved_execute_outcomes,
        counts.truth_outcomes,
        counts.survived_required_edge,
    )

    assert all(current <= previous for previous, current in zip(values, values[1:]))
    assert sum(row.counts.candidate_cycles for row in report.by_regime) == counts.candidate_cycles
    assert sum(row.counts.candidate_cycles for row in report.by_route) == counts.candidate_cycles


def test_zero_execute_population_is_valid_and_otr_is_unavailable_not_zero():
    case = _case(
        "funnel-negative",
        1,
        volatility="low",
        edge_bps=-10.0,
        realized_edge_bps=-12.0,
    )
    report = build_opportunity_funnel(ReplayBundle(cases=(case,)))

    assert report.overall.counts.candidate_cycles == 1
    assert report.overall.counts.complete_evidence == 1
    assert report.overall.counts.structural_constraints_pass == 1
    assert report.overall.counts.gross_positive == 0
    assert report.overall.counts.final_execute_sim == 0
    assert report.overall.observed_edge.count == 1
    assert report.first_blocker_counts == (("GROSS_NON_POSITIVE", 1),)
    assert "OTR is unavailable, not zero" in render_opportunity_funnel_markdown(report)


def test_modeled_cost_drag_is_separated_from_raw_gross_edge():
    base = _case(
        "funnel-cost-drag",
        1,
        volatility="low",
        edge_bps=20.0,
        realized_edge_bps=-20.0,
    )
    costs = CostAssumption(fee_bps=10.0, slippage_bps=2.0)
    case = replace(
        base,
        legs=tuple(replace(leg, costs=costs) for leg in base.legs),
    )
    report = build_opportunity_funnel(ReplayBundle(cases=(case,)))

    assert report.overall.counts.gross_positive == 1
    assert report.overall.counts.net_positive == 0
    assert report.overall.modeled_cost_drag.mean_bps == pytest.approx(
        36.02873091455905,
        abs=1e-12,
    )
    assert report.first_blocker_counts == (("MODELED_COSTS_ERASE_EDGE", 1),)
    assert report.economic_blocker_counts == (("MODELED_COSTS_ERASE_EDGE", 1),)


def test_capacity_failure_is_structural_not_economic():
    base = _case(
        "funnel-capacity",
        1,
        volatility="low",
        edge_bps=32.0,
        realized_edge_bps=32.0,
    )
    case = replace(base, start_amount=1_000_000_000.0)
    report = build_opportunity_funnel(ReplayBundle(cases=(case,)))

    assert report.overall.counts.complete_evidence == 1
    assert report.overall.counts.structural_constraints_pass == 0
    assert report.overall.counts.gross_positive == 0
    assert report.structural_blocker_counts
    assert any(
        reason.startswith("CAPACITY_EXCEEDED:")
        for reason, _ in report.structural_blocker_counts
    )
    assert report.economic_blocker_counts == ()


def test_report_tamper_is_rejected_even_with_recomputed_outer_digest():
    source = _bundle()
    report = build_opportunity_funnel(source)
    envelope = deepcopy(report.to_envelope())
    envelope["payload"]["overall"]["funnel"]["counts"]["candidate_cycles"] += 1
    envelope["sha256"] = _canonical_sha(envelope["payload"])

    with pytest.raises(ValueError, match="does not reproduce"):
        verify_opportunity_funnel_envelope(envelope, source=source)


def test_cli_builds_markdown_and_fully_verifies_real_corpus(tmp_path):
    source = tmp_path / "corpus.json"
    report = tmp_path / "funnel.json"
    markdown = tmp_path / "funnel.md"
    save_corpus(source, _real_corpus())

    assert funnel_main(
        [
            "build",
            str(source),
            "--output",
            str(report),
            "--markdown-output",
            str(markdown),
        ]
    ) == 0
    assert report.exists()
    assert markdown.exists()
    assert "Opportunity Funnel Benchmark" in markdown.read_text(encoding="utf-8")
    assert funnel_main(["verify", str(source), str(report)]) == 0
