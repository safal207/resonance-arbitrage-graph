from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .opportunity_truth_benchmark import (
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


def _load_bundle(path: str) -> tuple[ReplayBundle, str]:
    envelope = _load_json(path)
    payload = envelope.get("payload")
    if not isinstance(payload, dict):
        raise ValueError("input envelope is missing payload object")
    schema = payload.get("schema")
    if schema == "resonance.arbitrage.replay-bundle/v0.2":
        return ReplayBundle.from_envelope(envelope), "replay_bundle"
    if schema == "resonance.arbitrage.real-market-replay-corpus/v0.1":
        corpus = RealMarketReplayCorpus.from_envelope(envelope)
        return corpus.to_replay_bundle(), "real_market_corpus"
    raise ValueError("input must be a replay bundle or real-market replay corpus")


def _write_json(payload: dict[str, Any], path: str | None) -> None:
    rendered = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if path:
        Path(path).write_text(rendered, encoding="utf-8")
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
        bundle, source_kind = _load_bundle(args.input)
        report = build_opportunity_truth_benchmark(
            bundle,
            min_truth_population=args.min_truth_population,
        )
        envelope = report.to_envelope()
        _write_json(envelope, args.output)
        if args.markdown_output:
            Path(args.markdown_output).write_text(
                render_opportunity_truth_markdown(report),
                encoding="utf-8",
            )
        print(
            f"benchmark_status={report.status.value} source={source_kind} "
            f"truth_population={report.truth_population} sha256={report.sha256}",
        )
        return 0

    if args.command == "verify":
        bundle, _ = _load_bundle(args.input)
        verify_opportunity_truth_benchmark_envelope(
            _load_json(args.report),
            bundle=bundle,
        )
        print("OK")
        return 0

    raise RuntimeError("unreachable command")


if __name__ == "__main__":
    raise SystemExit(main())
