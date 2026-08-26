from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

from .opportunity_truth_benchmark import (
    OpportunityTruthBenchmarkReport,
    build_opportunity_truth_benchmark,
    build_opportunity_truth_benchmark_from_corpus,
    render_opportunity_truth_markdown,
    verify_opportunity_truth_benchmark_envelope,
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
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if path:
        _write_text(path, rendered)
    else:
        print(rendered, end="")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="resonance-opportunity-truth-benchmark",
        description="Build or verify the paper-only RESONANCE Verify Opportunity Truth Benchmark.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    build = sub.add_parser("build")
    build.add_argument("input")
    build.add_argument("--min-truth-population", type=int, default=30)
    build.add_argument("--output")
    build.add_argument("--markdown-output")

    verify = sub.add_parser("verify")
    verify.add_argument("input")
    verify.add_argument("report")

    return parser


def _build_report(
    source: ReplayBundle | RealMarketReplayCorpus,
    *,
    min_truth_population: int,
) -> OpportunityTruthBenchmarkReport:
    if isinstance(source, RealMarketReplayCorpus):
        return build_opportunity_truth_benchmark_from_corpus(
            source,
            min_truth_population=min_truth_population,
        )
    return build_opportunity_truth_benchmark(
        source,
        min_truth_population=min_truth_population,
    )


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)

    if args.command == "build":
        source = _load_source(args.input)
        report = _build_report(
            source,
            min_truth_population=args.min_truth_population,
        )
        _write_json(report.to_envelope(), args.output)
        if args.markdown_output:
            _write_text(
                args.markdown_output,
                render_opportunity_truth_markdown(report),
            )
        print(
            f"benchmark_status={report.status.value} source={report.evidence_source.value} "
            f"truth_population={report.truth_population} "
            f"public_claim_eligible={str(report.public_claim_eligible).lower()} "
            f"sha256={report.sha256}",
            file=sys.stderr,
        )
        return 0

    if args.command == "verify":
        source = _load_source(args.input)
        verify_opportunity_truth_benchmark_envelope(
            _load_json(args.report),
            source=source,
        )
        print("OK")
        return 0

    raise RuntimeError("unreachable command")


if __name__ == "__main__":
    raise SystemExit(main())
