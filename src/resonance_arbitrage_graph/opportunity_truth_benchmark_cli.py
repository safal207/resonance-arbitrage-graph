from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

from .opportunity_truth_benchmark import (
    OpportunityTruthEvidenceSource,
    build_opportunity_truth_benchmark,
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


def _load_bundle(
    path: str,
) -> tuple[ReplayBundle, OpportunityTruthEvidenceSource, str | None]:
    envelope = _load_json(path)
    payload = envelope.get("payload")
    if not isinstance(payload, dict):
        raise ValueError("input envelope is missing payload object")
    schema = payload.get("schema")
    if schema == "resonance.arbitrage.replay-bundle/v0.2":
        return (
            ReplayBundle.from_envelope(envelope),
            OpportunityTruthEvidenceSource.REPLAY_BUNDLE,
            None,
        )
    if schema == "resonance.arbitrage.real-market-replay-corpus/v0.1":
        corpus = RealMarketReplayCorpus.from_envelope(envelope)
        return (
            corpus.to_replay_bundle(),
            OpportunityTruthEvidenceSource.REAL_MARKET_CORPUS,
            corpus.sha256,
        )
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


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)

    if args.command == "build":
        bundle, source_kind, corpus_sha = _load_bundle(args.input)
        report = build_opportunity_truth_benchmark(
            bundle,
            min_truth_population=args.min_truth_population,
            evidence_source=source_kind,
            source_corpus_sha256=corpus_sha,
        )
        envelope = report.to_envelope()
        _write_json(envelope, args.output)
        if args.markdown_output:
            _write_text(
                args.markdown_output,
                render_opportunity_truth_markdown(report),
            )
        print(
            f"benchmark_status={report.status.value} source={source_kind.value} "
            f"truth_population={report.truth_population} "
            f"public_claim_eligible={str(report.public_claim_eligible).lower()} "
            f"sha256={report.sha256}",
            file=sys.stderr,
        )
        return 0

    if args.command == "verify":
        bundle, source_kind, corpus_sha = _load_bundle(args.input)
        verify_opportunity_truth_benchmark_envelope(
            _load_json(args.report),
            bundle=bundle,
            evidence_source=source_kind,
            source_corpus_sha256=corpus_sha,
        )
        print("OK")
        return 0

    raise RuntimeError("unreachable command")


if __name__ == "__main__":
    raise SystemExit(main())
