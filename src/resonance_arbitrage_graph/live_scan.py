from __future__ import annotations

import argparse
from collections.abc import Callable, Sequence
import json
import time

from .adapters import BinanceBookTickerAdapter, KrakenPreTradeAdapter
from .model import Node
from .quotes import CostAssumption, QuoteSnapshot
from .rolling_state import RollingMarketWindow, RollingWindowPolicy
from .scanner import scan_cycles
from .window_evidence import make_window_regime_evidence_receipt
from .window_regime import market_key


def _parse_pair(value: str) -> tuple[str, str, str]:
    parts = value.split(":")
    if len(parts) != 3 or not all(parts):
        raise argparse.ArgumentTypeError("pair must be SYMBOL:BASE:QUOTE")
    return parts[0], parts[1].upper(), parts[2].upper()


def _fetch_round(adapter, pairs: Sequence[tuple[str, str, str]]) -> list[QuoteSnapshot]:
    if adapter.venue == BinanceBookTickerAdapter.venue:
        return [
            adapter.fetch(symbol, base_asset=base, quote_asset=quote)
            for symbol, base, quote in pairs
        ]

    snapshots = [adapter.fetch(symbol) for symbol, _base, _quote in pairs]
    for snapshot, (_symbol, expected_base, expected_quote) in zip(snapshots, pairs):
        if (snapshot.base_asset, snapshot.quote_asset) != (expected_base, expected_quote):
            raise ValueError(
                f"Kraken normalized pair mismatch: got {snapshot.base_asset}/{snapshot.quote_asset}, "
                f"expected {expected_base}/{expected_quote}"
            )
    return snapshots


def _collect_rolling_quotes(
    adapter,
    pairs: Sequence[tuple[str, str, str]],
    *,
    sample_count: int,
    interval_ms: int,
    sleep_fn: Callable[[float], None] = time.sleep,
) -> tuple[list[QuoteSnapshot], dict[str, list[QuoteSnapshot]]]:
    if sample_count < 3:
        raise ValueError("rolling sample count must be >= 3")
    if interval_ms < 1:
        raise ValueError("rolling sample interval must be >= 1 ms")

    history: dict[str, list[QuoteSnapshot]] = {}
    latest: list[QuoteSnapshot] = []
    for round_index in range(sample_count):
        latest = _fetch_round(adapter, pairs)
        for snapshot in latest:
            history.setdefault(market_key(snapshot.venue, snapshot.symbol), []).append(snapshot)
        if round_index + 1 < sample_count:
            sleep_fn(interval_ms / 1000.0)
    return latest, history


def main() -> int:
    parser = argparse.ArgumentParser(description="RESONANCE paper-only live market scan")
    parser.add_argument("--venue", choices=("binance", "kraken"), required=True)
    parser.add_argument("--pair", action="append", type=_parse_pair, required=True)
    parser.add_argument("--start-asset", required=True)
    parser.add_argument("--amount", type=float, required=True)
    parser.add_argument("--fee-bps", type=float, required=True, help="explicit paper-model fee assumption")
    parser.add_argument("--slippage-bps", type=float, required=True, help="explicit paper-model slippage assumption")
    parser.add_argument("--max-hops", type=int, default=3)
    parser.add_argument("--rolling-samples", type=int, default=5)
    parser.add_argument("--rolling-interval-ms", type=int, default=1_000)
    parser.add_argument("--rolling-horizon-ms", type=int, default=5_000)
    parser.add_argument("--rolling-min-coverage-ratio", type=float, default=0.8)
    args = parser.parse_args()

    adapter = BinanceBookTickerAdapter() if args.venue == "binance" else KrakenPreTradeAdapter()
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

    now_ms = time.time_ns() // 1_000_000
    costs = CostAssumption(fee_bps=args.fee_bps, slippage_bps=args.slippage_bps)
    opportunities = scan_cycles(
        quotes,
        start=Node(adapter.venue, args.start_asset.upper()),
        amount=args.amount,
        costs_by_venue={adapter.venue: costs},
        now_ms=now_ms,
        max_hops=args.max_hops,
    )

    opportunity_payloads = []
    for index, item in enumerate(opportunities):
        operation_id = f"live-scan-{adapter.venue}-{now_ms}-{index}"
        receipt = make_window_regime_evidence_receipt(
            operation_id,
            item.route,
            item.result,
            snapshots=quotes,
            windows_by_market=windows,
            evaluation_time_ms=now_ms,
        )
        opportunity_payloads.append(
            {
                "logical_operation_id": operation_id,
                "route": [f"{edge.src.key}->{edge.dst.key}" for edge in item.route],
                "verdict": item.result.verdict.value,
                "gross_edge": item.result.gross_edge,
                "net_edge": item.result.net_edge,
                "risk_adjusted_edge": item.result.risk_adjusted_edge,
                "success_probability": item.result.success_probability,
                "reasons": list(item.result.reasons),
                "market_regime": receipt.payload["market_regime"],
                "rolling_market_state": {
                    key: {
                        "sha256": value["sha256"],
                        "summary": value["summary"],
                    }
                    for key, value in receipt.payload["rolling_market_state"]["markets"].items()
                },
                "evidence_sha256": receipt.sha256,
                "market_bindings": receipt.payload["market_bindings"],
            }
        )

    output = {
        "paper_only": True,
        "venue": adapter.venue,
        "scan_observed_at_ms": now_ms,
        "cost_assumptions": {
            "fee_bps": costs.fee_bps,
            "slippage_bps": costs.slippage_bps,
            "gas_bps": costs.gas_bps,
        },
        "rolling_window_policy": {
            "horizon_ms": window_policy.horizon_ms,
            "min_samples": window_policy.min_samples,
            "min_coverage_ratio": window_policy.min_coverage_ratio,
            "sample_interval_ms": args.rolling_interval_ms,
        },
        "quotes": [
            {
                "symbol": quote.symbol,
                "base_asset": quote.base_asset,
                "quote_asset": quote.quote_asset,
                "bid_price": quote.bid_price,
                "bid_qty": quote.bid_qty,
                "ask_price": quote.ask_price,
                "ask_qty": quote.ask_qty,
                "observed_at_ms": quote.observed_at_ms,
                "source_timestamp_ms": quote.source_timestamp_ms,
                "timestamp_class": quote.timestamp_class,
                "source_url": quote.source_url,
                "metadata_url": quote.metadata_url,
            }
            for quote in quotes
        ],
        "opportunities": opportunity_payloads,
    }
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
