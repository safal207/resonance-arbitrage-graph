from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .corpus_quality import CorpusQualityPolicy
from .opportunity_truth_benchmark import (
    BenchmarkClaimPolicy,
    OpportunityTruthBenchmarkReport,
    build_opportunity_truth_benchmark,
    render_opportunity_truth_benchmark_markdown,
    verify_opportunity_truth_benchmark_envelope,
    verify_opportunity_truth_benchmark_source_binding,
)
from .real_market_corpus import RealMarketReplayCorpus
from .replay import ReplayBundle


def _load_json(path: str | Path) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _write(text: str, output: str | None) -> None:
    if output:
        destination = Path(output)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(text, encoding="utf-8")
    else:
        print(text, end="")


def _load_source(path: str | Path) -> RealMarketReplayCorpus | ReplayBundle:
    envelope = _load_json(path)
    payload = envelope.get("payload")
    if not isinstance(payload, dict):
        raise ValueError("source envelope payload must be an object")
    schema = payload.get("schema")
    if schema == "resonance.arbitrage.real-market-replay-corpus/v0.1":
        return RealMarketReplayCorpus.from_envelope(envelope)
    if schema == "resonance.arbitrage.replay-bundle/v0.2":
        return ReplayBundle.from_envelope(envelope)
    raise ValueError("source must be a real-market corpus or replay bundle envelope")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="resonance-opportunity-truth-benchmark",
        description=(
            "Build and verify deterministic paper-only Opportunity Truth Benchmark reports."
        ),
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    build = subparsers.add_parser("build")
    build.add_argument("source", help="real-market corpus or replay-bundle envelope")
    build.add_argument("--format", choices=("json", "markdown"), default="json")
    build.add_argument("--output")
    build.add_argument("--min-terminal-operations", type=int, default=100)
    build.add_argument("--min-truth-events", type=int, default=30)
    build.add_argument(
        "--ignore-corpus-quality",
        action="store_true",
        help="do not require the corpus quality gate for internal claim readiness",
    )
    build.add_argument("--min-decision-batches", type=int, default=20)
    build.add_argument("--min-effective-decision-batches", type=float, default=10.0)
    build.add_argument("--min-temporal-span-ms", type=int, default=3_600_000)
    build.add_argument("--min-distinct-routes", type=int, default=3)
    build.add_argument("--min-effective-routes", type=float, default=2.0)
    build.add_argument("--min-distinct-route-markets", type=int, default=3)
    build.add_argument("--min-distinct-regimes", type=int, default=2)

    verify = subparsers.add_parser("verify")
    verify.add_argument("report", help="benchmark JSON envelope")
    verify.add_argument("source", help="bound real-market corpus or replay bundle")

    render = subparsers.add_parser("render")
    render.add_argument("report", help="benchmark JSON envelope")
    render.add_argument("--output")

    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    if args.command == "build":
        source = _load_source(args.source)
        claim_policy = BenchmarkClaimPolicy(
            min_terminal_operations=args.min_terminal_operations,
            min_truth_events=args.min_truth_events,
            require_corpus_quality=not args.ignore_corpus_quality,
        )
        quality_policy = CorpusQualityPolicy(
            min_decision_batches=args.min_decision_batches,
            min_effective_decision_batches=args.min_effective_decision_batches,
            min_temporal_span_ms=args.min_temporal_span_ms,
            min_distinct_routes=args.min_distinct_routes,
            min_effective_routes=args.min_effective_routes,
            min_distinct_route_markets=args.min_distinct_route_markets,
            min_distinct_regimes=args.min_distinct_regimes,
        )
        report = build_opportunity_truth_benchmark(
            source,
            claim_policy=claim_policy,
            quality_policy=(
                quality_policy if isinstance(source, RealMarketReplayCorpus) else None
            ),
        )
        if args.format == "markdown":
            _write(render_opportunity_truth_benchmark_markdown(report), args.output)
        else:
            rendered = (
                json.dumps(
                    report.to_envelope(),
                    sort_keys=True,
                    indent=2,
                    ensure_ascii=False,
                    allow_nan=False,
                )
                + "\n"
            )
            _write(rendered, args.output)
        return 0

    if args.command == "verify":
        envelope = _load_json(args.report)
        verify_opportunity_truth_benchmark_envelope(envelope)
        verify_opportunity_truth_benchmark_source_binding(
            envelope,
            _load_source(args.source),
        )
        print("FULL_OK")
        return 0

    if args.command == "render":
        payload = verify_opportunity_truth_benchmark_envelope(
            _load_json(args.report)
        )
        report = OpportunityTruthBenchmarkReport.from_payload(payload)
        _write(render_opportunity_truth_benchmark_markdown(report), args.output)
        return 0

    raise RuntimeError("unreachable command")


if __name__ == "__main__":
    raise SystemExit(main())
