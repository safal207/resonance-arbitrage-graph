from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

from .opportunity_funnel import (
    build_opportunity_funnel,
    render_opportunity_funnel_markdown,
    verify_opportunity_funnel_envelope,
)
from .real_market_corpus import RealMarketReplayCorpus
from .replay import ReplayBundle


def _load_json(path: str) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _load_source(path: str) -> RealMarketReplayCorpus | ReplayBundle:
    envelope = _load_json(path)
    payload = envelope.get("payload")
    if not isinstance(payload, dict):
        raise ValueError("input envelope is missing payload object")
    schema = payload.get("schema")
    if schema == "resonance.arbitrage.real-market-replay-corpus/v0.1":
        return RealMarketReplayCorpus.from_envelope(envelope)
    if schema == "resonance.arbitrage.replay-bundle/v0.2":
        return ReplayBundle.from_envelope(envelope)
    raise ValueError("input must be a real-market corpus or replay bundle")


def _write(path: str, content: str) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(content, encoding="utf-8")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="resonance-opportunity-funnel",
        description="Build or verify the paper-only RESONANCE opportunity funnel.",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    build = commands.add_parser("build")
    build.add_argument("input")
    build.add_argument("--output")
    build.add_argument("--markdown-output")

    verify = commands.add_parser("verify")
    verify.add_argument("input")
    verify.add_argument("report")

    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    source = _load_source(args.input)

    if args.command == "build":
        report = build_opportunity_funnel(source)
        rendered = json.dumps(report.to_envelope(), indent=2, sort_keys=True) + "\n"
        if args.output:
            _write(args.output, rendered)
        else:
            print(rendered, end="")
        if args.markdown_output:
            _write(
                args.markdown_output,
                render_opportunity_funnel_markdown(report),
            )
        print(
            " ".join(
                (
                    f"candidates={report.overall.counts.candidate_cycles}",
                    f"gross_positive={report.overall.counts.gross_positive}",
                    f"final_execute_sim={report.overall.counts.final_execute_sim}",
                    f"sha256={report.sha256}",
                )
            ),
            file=sys.stderr,
        )
        return 0

    if args.command == "verify":
        verify_opportunity_funnel_envelope(
            _load_json(args.report),
            source=source,
        )
        print("OK")
        return 0

    raise RuntimeError("unreachable command")


if __name__ == "__main__":
    raise SystemExit(main())
