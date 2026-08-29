from __future__ import annotations

import argparse
import json
from pathlib import Path

from .adapters import BinanceBookTickerAdapter, KrakenPreTradeAdapter
from .corpus_campaign import run_resumable_campaign_step
from .corpus_quality import CorpusQualityPolicy
from .corpus_runner import CorpusRunnerConfig
from .engine import Policy
from .live_scan import _parse_pair
from .quotes import CostAssumption


def _adapter(venue: str):
    if venue == "binance":
        return BinanceBookTickerAdapter()
    return KrakenPreTradeAdapter()


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="resonance-corpus-campaign-step",
        description=(
            "Recover matured pending public-market decisions, then run one new "
            "paper-only corpus capture/outcome step."
        ),
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
    parser.add_argument("--gas-bps", type=float, default=0.0)

    parser.add_argument("--execute-net-edge-bps", type=float, default=30.0)
    parser.add_argument("--observe-net-edge-bps", type=float, default=0.0)
    parser.add_argument("--max-quote-age-ms", type=int, default=3_000)
    parser.add_argument("--max-route-latency-ms", type=int, default=5_000)
    parser.add_argument("--min-success-probability", type=float, default=0.75)

    parser.add_argument("--horizon-ms", type=int, default=60_000)
    parser.add_argument("--max-hops", type=int, default=3)
    parser.add_argument("--max-cases", type=int, default=20)
    parser.add_argument("--rolling-samples", type=int, default=5)
    parser.add_argument("--rolling-interval-ms", type=int, default=1_000)
    parser.add_argument("--rolling-horizon-ms", type=int, default=5_000)
    parser.add_argument("--rolling-min-coverage-ratio", type=float, default=0.8)
    parser.add_argument("--min-terminal-operations", type=int, default=100)
    parser.add_argument("--min-training-rows", type=int, default=20)

    quality = parser.add_argument_group("corpus quality gate")
    quality.add_argument("--min-decision-batches", type=int, default=20)
    quality.add_argument(
        "--min-effective-decision-batches",
        type=float,
        default=10.0,
    )
    quality.add_argument("--min-temporal-span-ms", type=int, default=3_600_000)
    quality.add_argument("--min-distinct-routes", type=int, default=3)
    quality.add_argument("--min-effective-routes", type=float, default=2.0)
    quality.add_argument("--min-distinct-route-markets", type=int, default=3)
    quality.add_argument("--min-distinct-regimes", type=int, default=2)
    return parser


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(
        json.dumps(
            payload,
            indent=2,
            sort_keys=True,
            ensure_ascii=False,
            allow_nan=False,
        )
        + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    quality_policy = CorpusQualityPolicy(
        min_decision_batches=args.min_decision_batches,
        min_effective_decision_batches=args.min_effective_decision_batches,
        min_temporal_span_ms=args.min_temporal_span_ms,
        min_distinct_routes=args.min_distinct_routes,
        min_effective_routes=args.min_effective_routes,
        min_distinct_route_markets=args.min_distinct_route_markets,
        min_distinct_regimes=args.min_distinct_regimes,
    )
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
        quality_policy=quality_policy,
        benchmark_when_ready=False,
    )
    result = run_resumable_campaign_step(
        corpus_path=args.corpus,
        replay_output_path=args.replay_output,
        adapter=_adapter(args.venue),
        pairs=tuple(args.pair),
        start_asset=args.start_asset,
        amount=args.amount,
        costs=CostAssumption(
            fee_bps=args.fee_bps,
            slippage_bps=args.slippage_bps,
            gas_bps=args.gas_bps,
        ),
        config=config,
        engine_policy=Policy(
            execute_net_edge=args.execute_net_edge_bps / 10_000.0,
            observe_net_edge=args.observe_net_edge_bps / 10_000.0,
            max_quote_age_ms=args.max_quote_age_ms,
            max_route_latency_ms=args.max_route_latency_ms,
            min_success_probability=args.min_success_probability,
        ),
    )
    envelope = result.to_envelope()
    if args.receipt_output is not None:
        _write(args.receipt_output, envelope)
    print(
        json.dumps(
            envelope,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
