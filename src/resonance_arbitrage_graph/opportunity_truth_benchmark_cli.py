from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

from .corpus_quality import CorpusQualityPolicy
from .opportunity_truth_benchmark_v2 import (
    OpportunityTruthBenchmarkV2Report,
    OpportunityTruthClaimPolicy,
    build_opportunity_truth_benchmark_v2,
    render_opportunity_truth_benchmark_v2_markdown,
    verify_opportunity_truth_benchmark_v2_envelope,
    verify_opportunity_truth_benchmark_v2_source_binding,
)
from .real_market_corpus import RealMarketReplayCorpus
from .replay import ReplayBundle


def _load_json(path: str) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _load_source(path: str) -> ReplayBundle | RealMarketReplayCorpus:
    envelope = _load_json(path)
    payload = envelope.get("payload")
    if not isinstance(payload, dict):
        raise ValueError("input envelope is missing payload object")
    schema = payload.get("schema")
    if schema == "resonance.arbitrage.replay-bundle/v0.2":
        return ReplayBundle.from_envelope(envelope)
    if schema == "resonance.arbitrage.real-market-replay-corpus/v0.1":
        return RealMarketReplayCorpus.from_envelope(envelope)
    raise ValueError("input must be a replay bundle or real-market replay corpus")


def _write_text(path: str, content: str) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(content, encoding="utf-8")


def _write_json(payload: dict[str, Any], path: str | None) -> None:
    rendered = (
        json.dumps(
            payload,
            indent=2,
            sort_keys=True,
            ensure_ascii=False,
            allow_nan=False,
        )
        + "\n"
    )
    if path:
        _write_text(path, rendered)
    else:
        print(rendered, end="")


def _add_quality_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--min-decision-batches", type=int, default=20)
    parser.add_argument(
        "--min-effective-decision-batches", type=float, default=10.0
    )
    parser.add_argument("--min-temporal-span-ms", type=int, default=3_600_000)
    parser.add_argument("--min-distinct-routes", type=int, default=3)
    parser.add_argument("--min-effective-routes", type=float, default=2.0)
    parser.add_argument("--min-distinct-route-markets", type=int, default=3)
    parser.add_argument("--min-distinct-regimes", type=int, default=2)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="resonance-opportunity-truth-benchmark",
        description=(
            "Build or verify the paper-only RESONANCE Verify "
            "Opportunity Truth Benchmark v0.2."
        ),
    )
    sub = parser.add_subparsers(dest="command", required=True)

    build = sub.add_parser("build")
    build.add_argument("input")
    build.add_argument("--min-terminal-operations", type=int, default=100)
    build.add_argument("--min-truth-population", type=int, default=30)
    build.add_argument(
        "--ignore-corpus-quality",
        action="store_true",
        help=(
            "allow internal readiness without the real-market "
            "corpus-quality gate"
        ),
    )
    _add_quality_arguments(build)
    build.add_argument("--output")
    build.add_argument("--markdown-output")

    verify = sub.add_parser("verify")
    verify.add_argument("input")
    verify.add_argument("report")

    render = sub.add_parser("render")
    render.add_argument("report")
    render.add_argument("--output")

    return parser


def _quality_policy(args: argparse.Namespace) -> CorpusQualityPolicy:
    return CorpusQualityPolicy(
        min_decision_batches=args.min_decision_batches,
        min_effective_decision_batches=args.min_effective_decision_batches,
        min_temporal_span_ms=args.min_temporal_span_ms,
        min_distinct_routes=args.min_distinct_routes,
        min_effective_routes=args.min_effective_routes,
        min_distinct_route_markets=args.min_distinct_route_markets,
        min_distinct_regimes=args.min_distinct_regimes,
    )


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)

    if args.command == "build":
        source = _load_source(args.input)
        report = build_opportunity_truth_benchmark_v2(
            source,
            claim_policy=OpportunityTruthClaimPolicy(
                min_terminal_operations=args.min_terminal_operations,
                min_truth_events=args.min_truth_population,
                require_corpus_quality=not args.ignore_corpus_quality,
            ),
            quality_policy=(
                _quality_policy(args)
                if isinstance(source, RealMarketReplayCorpus)
                else None
            ),
        )
        _write_json(report.to_envelope(), args.output)
        if args.markdown_output:
            _write_text(
                args.markdown_output,
                render_opportunity_truth_benchmark_v2_markdown(report),
            )
        print(
            f"claim_status={report.claim_status.value} "
            f"source={report.evidence_source.value} "
            f"terminal_operations={report.terminal_operations} "
            f"truth_population={report.truth_population} "
            f"internal_evidence_ready="
            f"{str(report.internal_evidence_ready).lower()} "
            f"sha256={report.sha256}",
            file=sys.stderr,
        )
        return 0

    if args.command == "verify":
        source = _load_source(args.input)
        envelope = _load_json(args.report)
        verify_opportunity_truth_benchmark_v2_envelope(envelope)
        verify_opportunity_truth_benchmark_v2_source_binding(
            envelope,
            source,
        )
        print("FULL_OK")
        return 0

    if args.command == "render":
        payload = verify_opportunity_truth_benchmark_v2_envelope(
            _load_json(args.report)
        )
        report = OpportunityTruthBenchmarkV2Report(
            evidence_source=__import__(
                "resonance_arbitrage_graph.opportunity_truth_benchmark",
                fromlist=["OpportunityTruthEvidenceSource"],
            ).OpportunityTruthEvidenceSource(payload["evidence_source"]),
            source_sha256=payload["source_sha256"],
            replay_bundle_sha256=payload["replay_bundle_sha256"],
            operation_ids=tuple(payload["operation_ids"]),
            legacy_benchmark=payload["legacy_benchmark"],
            legacy_benchmark_sha256=payload["legacy_benchmark_sha256"],
            claim_policy=OpportunityTruthClaimPolicy.from_payload(
                payload["claim_policy"]
            ),
            claim_status=__import__(
                "resonance_arbitrage_graph.opportunity_truth_benchmark_v2",
                fromlist=["OpportunityTruthClaimStatus"],
            ).OpportunityTruthClaimStatus(payload["claim_status"]),
            claim_reasons=tuple(payload["claim_reasons"]),
            corpus_quality=payload["corpus_quality"],
            corpus_quality_sha256=payload["corpus_quality_sha256"],
            terminal_operations=payload["terminal_operations"],
            truth_population=payload["truth_population"],
            truth_coverage=payload["truth_coverage"],
            mean_expected_edge_bps=payload["mean_expected_edge_bps"],
            mean_observed_edge_bps=payload["mean_observed_edge_bps"],
            mean_edge_decay_bps=payload["mean_edge_decay_bps"],
            paper_pnl_by_start_state=tuple(
                __import__(
                    "resonance_arbitrage_graph.opportunity_truth_benchmark_v2",
                    fromlist=["OpportunityTruthPnlSlice"],
                ).OpportunityTruthPnlSlice.from_payload(item)
                for item in payload["paper_pnl_by_start_state"]
            ),
        )
        rendered = render_opportunity_truth_benchmark_v2_markdown(report)
        if args.output:
            _write_text(args.output, rendered)
        else:
            print(rendered, end="")
        return 0

    raise RuntimeError("unreachable command")


if __name__ == "__main__":
    raise SystemExit(main())
