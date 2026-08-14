from __future__ import annotations

import argparse
import json
import time

from .adapters import BinanceBookTickerAdapter, KrakenPreTradeAdapter
from .engine import Policy
from .live_scan import _collect_rolling_quotes, _fetch_round, _parse_pair
from .model import Node
from .quotes import CostAssumption
from .real_market_corpus import (
    build_decision_cases,
    export_replay_bundle,
    load_corpus,
    resolve_replay_case,
    save_corpus,
)
from .regime import RegimePolicy
from .regime_gate import RegimeExecutionPolicy
from .rolling_state import RollingMarketWindow, RollingWindowPolicy
from .scanner import scan_cycles


def _adapter(venue: str):
    return (
        BinanceBookTickerAdapter()
        if venue == "binance"
        else KrakenPreTradeAdapter()
    )


def _add_market_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--venue", choices=("binance", "kraken"), required=True)
    parser.add_argument("--pair", action="append", type=_parse_pair, required=True)


def _summary(corpus) -> dict[str, object]:
    pending = corpus.pending_cases()
    terminal_operations = {
        record.replay_case.logical_operation_id
        for record in corpus.records
        if record.replay_case.outcome.terminal
    }
    return {
        "paper_only": True,
        "public_market_data_only": True,
        "record_count": len(corpus.records),
        "operation_count": len(
            {record.replay_case.logical_operation_id for record in corpus.records}
        ),
        "pending_operation_count": len(pending),
        "terminal_operation_count": len(terminal_operations),
        "corpus_sha256": corpus.sha256,
    }


def _capture(args: argparse.Namespace) -> int:
    adapter = _adapter(args.venue)
    quotes, history = _collect_rolling_quotes(
        adapter,
        args.pair,
        sample_count=args.rolling_samples,
        interval_ms=args.rolling_interval_ms,
    )
    window_policy = RollingWindowPolicy(
        horizon_ms=args.rolling_horizon_ms,
        min_samples=args.rolling_samples,
        min_coverage_ratio=args.rolling_min_coverage_ratio,
    )
    windows = {
        key: RollingMarketWindow.from_quotes(
            samples,
            policy=window_policy,
            end_ms=samples[-1].observed_at_ms,
        )
        for key, samples in history.items()
    }

    evaluation_time_ms = time.time_ns() // 1_000_000
    costs = CostAssumption(
        fee_bps=args.fee_bps,
        slippage_bps=args.slippage_bps,
    )
    engine_policy = Policy()
    opportunities = scan_cycles(
        quotes,
        start=Node(adapter.venue, args.start_asset.upper()),
        amount=args.amount,
        costs_by_venue={adapter.venue: costs},
        now_ms=evaluation_time_ms,
        max_hops=args.max_hops,
        policy=engine_policy,
    )
    selected = tuple(opportunities[: args.max_cases])
    if not selected:
        raise ValueError("public scan produced no cycle candidates to record")

    cases = build_decision_cases(
        quotes,
        windows,
        selected,
        costs_by_venue={adapter.venue: costs},
        evaluation_time_ms=evaluation_time_ms,
        start_amount=args.amount,
        engine_policy=engine_policy,
        regime_policy=RegimePolicy(),
        regime_execution_policy=RegimeExecutionPolicy(),
        operation_prefix=f"real-market-{adapter.venue}",
    )
    corpus = load_corpus(args.corpus)
    corpus = corpus.append_decisions(cases, captured_at_ms=evaluation_time_ms)
    save_corpus(args.corpus, corpus)

    payload = _summary(corpus)
    payload.update(
        {
            "action": "capture",
            "appended_decisions": len(cases),
            "scan_observed_at_ms": evaluation_time_ms,
            "captured_operation_ids": [
                case.logical_operation_id for case in cases
            ],
        }
    )
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


def _resolve(args: argparse.Namespace) -> int:
    corpus = load_corpus(args.corpus)
    pending = corpus.pending_cases()
    requested = set(args.operation_id or ())
    if requested:
        pending = tuple(
            case for case in pending if case.logical_operation_id in requested
        )
        missing = requested - {case.logical_operation_id for case in pending}
        if missing:
            raise ValueError(
                "requested operations are not pending: " + ", ".join(sorted(missing))
            )
    if not pending:
        raise ValueError("corpus has no pending operations to resolve")

    adapter = _adapter(args.venue)
    outcome_snapshots = tuple(_fetch_round(adapter, args.pair))
    observed_at_ms = max(
        time.time_ns() // 1_000_000,
        *(snapshot.observed_at_ms for snapshot in outcome_snapshots),
    )

    resolved_ids: list[str] = []
    skipped: dict[str, str] = {}
    for pending_case in pending:
        try:
            terminal = resolve_replay_case(
                pending_case,
                outcome_snapshots,
                observed_at_ms=observed_at_ms,
            )
        except ValueError as exc:
            if requested:
                raise
            skipped[pending_case.logical_operation_id] = str(exc)
            continue
        corpus = corpus.append_outcome(
            terminal,
            outcome_snapshots,
            captured_at_ms=observed_at_ms,
        )
        resolved_ids.append(pending_case.logical_operation_id)

    if not resolved_ids:
        raise ValueError("fresh public quotes did not match any pending route")
    save_corpus(args.corpus, corpus)

    payload = _summary(corpus)
    payload.update(
        {
            "action": "resolve",
            "outcome_observed_at_ms": observed_at_ms,
            "resolved_operation_ids": resolved_ids,
            "skipped_operations": skipped,
        }
    )
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


def _verify(args: argparse.Namespace) -> int:
    corpus = load_corpus(args.corpus)
    payload = _summary(corpus)
    payload["action"] = "verify"
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


def _export(args: argparse.Namespace) -> int:
    corpus = load_corpus(args.corpus)
    export_replay_bundle(args.output, corpus)
    payload = _summary(corpus)
    payload.update(
        {
            "action": "export",
            "output": args.output,
            "replay_bundle_sha256": corpus.to_replay_bundle().sha256,
        }
    )
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="RESONANCE append-only public real-market replay corpus"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    capture = subparsers.add_parser(
        "capture",
        help="capture decision-time public market evidence",
    )
    capture.add_argument("--corpus", required=True)
    _add_market_args(capture)
    capture.add_argument("--start-asset", required=True)
    capture.add_argument("--amount", type=float, required=True)
    capture.add_argument("--fee-bps", type=float, required=True)
    capture.add_argument("--slippage-bps", type=float, required=True)
    capture.add_argument("--max-hops", type=int, default=3)
    capture.add_argument("--max-cases", type=int, default=20)
    capture.add_argument("--rolling-samples", type=int, default=5)
    capture.add_argument("--rolling-interval-ms", type=int, default=1_000)
    capture.add_argument("--rolling-horizon-ms", type=int, default=5_000)
    capture.add_argument("--rolling-min-coverage-ratio", type=float, default=0.8)
    capture.set_defaults(handler=_capture)

    resolve = subparsers.add_parser(
        "resolve",
        help="append later public-quote outcomes for pending operations",
    )
    resolve.add_argument("--corpus", required=True)
    _add_market_args(resolve)
    resolve.add_argument("--operation-id", action="append")
    resolve.set_defaults(handler=_resolve)

    verify = subparsers.add_parser(
        "verify",
        help="verify corpus envelope, hash chain, replay identity and outcomes",
    )
    verify.add_argument("--corpus", required=True)
    verify.set_defaults(handler=_verify)

    export = subparsers.add_parser(
        "export",
        help="export the corpus into the canonical ReplayBundle envelope",
    )
    export.add_argument("--corpus", required=True)
    export.add_argument("--output", required=True)
    export.set_defaults(handler=_export)

    args = parser.parse_args()
    if getattr(args, "max_cases", 1) < 1:
        parser.error("--max-cases must be >= 1")
    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
