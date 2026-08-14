from __future__ import annotations

import argparse
import json
from pathlib import Path

from .adapters import BinanceBookTickerAdapter, KrakenPreTradeAdapter
from .corpus_runner import CorpusRunnerConfig, run_one_shot, save_runner_result
from .live_scan import _parse_pair
from .quotes import CostAssumption


def _adapter(venue: str):
    return (
        BinanceBookTickerAdapter()
        if venue == "binance"
        else KrakenPreTradeAdapter()
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run one public-data paper research cycle: capture -> horizon -> "
            "resolve -> verify -> export, with an explicit research-readiness gate."
        )
    )
    parser.add_argument("--corpus", type=Path, required=True)
    parser.add_argument("--replay-output", type=Path, required=True)
    parser.add_argument("--receipt-output", type=Path)
    parser.add_argument("--venue", choices=("binance", "kraken"), required=True)
    parser.add_argument("--pair", action="append", type=_parse_pair, required=True)
    parser.add_argument("--start-asset", required=True)
    parser.add_argument("--amount", type=float, required=True)
    parser.add_argument("--fee-bps", type=float, required=True)
    parser.add_argument("--slippage-bps", type=float, required=True)
    parser.add_argument("--horizon-ms", type=int, default=60_000)
    parser.add_argument("--max-hops", type=int, default=3)
    parser.add_argument("--max-cases", type=int, default=20)
    parser.add_argument("--rolling-samples", type=int, default=5)
    parser.add_argument("--rolling-interval-ms", type=int, default=1_000)
    parser.add_argument("--rolling-horizon-ms", type=int, default=5_000)
    parser.add_argument("--rolling-min-coverage-ratio", type=float, default=0.8)
    parser.add_argument("--min-terminal-operations", type=int, default=100)
    parser.add_argument("--min-training-rows", type=int, default=20)
    parser.add_argument(
        "--benchmark-when-ready",
        action="store_true",
        help=(
            "when the terminal-operation threshold is reached, run the existing "
            "leakage-safe CatBoost walk-forward benchmark; requires ml-catboost extra"
        ),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    config = CorpusRunnerConfig(
        horizon_ms=args.horizon_ms,
        max_hops=args.max_hops,
        max_cases=args.max_cases,
        rolling_samples=args.rolling_samples,
        rolling_interval_ms=args.rolling_interval_ms,
        rolling_horizon_ms=args.rolling_horizon_ms,
        rolling_min_coverage_ratio=args.rolling_min_coverage_ratio,
        min_terminal_operations=args.min_terminal_operations,
        min_training_rows=args.min_training_rows,
        benchmark_when_ready=args.benchmark_when_ready,
    )
    result = run_one_shot(
        corpus_path=args.corpus,
        replay_output_path=args.replay_output,
        adapter=_adapter(args.venue),
        pairs=tuple(args.pair),
        start_asset=args.start_asset,
        amount=args.amount,
        costs=CostAssumption(
            fee_bps=args.fee_bps,
            slippage_bps=args.slippage_bps,
        ),
        config=config,
    )
    if args.receipt_output is not None:
        save_runner_result(args.receipt_output, result)
    print(
        json.dumps(
            result.to_envelope(),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
