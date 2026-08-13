from __future__ import annotations

import argparse
import json
import time

from .adapters import BinanceBookTickerAdapter, KrakenPreTradeAdapter
from .model import Node
from .quotes import CostAssumption
from .scanner import scan_cycles


def _parse_pair(value: str) -> tuple[str, str, str]:
    parts = value.split(":")
    if len(parts) != 3 or not all(parts):
        raise argparse.ArgumentTypeError("pair must be SYMBOL:BASE:QUOTE")
    return parts[0], parts[1].upper(), parts[2].upper()


def main() -> int:
    parser = argparse.ArgumentParser(description="RESONANCE paper-only live market scan")
    parser.add_argument("--venue", choices=("binance", "kraken"), required=True)
    parser.add_argument("--pair", action="append", type=_parse_pair, required=True)
    parser.add_argument("--start-asset", required=True)
    parser.add_argument("--amount", type=float, required=True)
    parser.add_argument("--fee-bps", type=float, required=True, help="explicit paper-model fee assumption")
    parser.add_argument("--slippage-bps", type=float, required=True, help="explicit paper-model slippage assumption")
    parser.add_argument("--max-hops", type=int, default=3)
    args = parser.parse_args()

    if args.venue == "binance":
        adapter = BinanceBookTickerAdapter()
        quotes = [
            adapter.fetch(symbol, base_asset=base, quote_asset=quote)
            for symbol, base, quote in args.pair
        ]
    else:
        adapter = KrakenPreTradeAdapter()
        quotes = [adapter.fetch(symbol) for symbol, _base, _quote in args.pair]
        for snapshot, (_symbol, expected_base, expected_quote) in zip(quotes, args.pair):
            if (snapshot.base_asset, snapshot.quote_asset) != (expected_base, expected_quote):
                raise ValueError(
                    f"Kraken normalized pair mismatch: got {snapshot.base_asset}/{snapshot.quote_asset}, "
                    f"expected {expected_base}/{expected_quote}"
                )

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

    output = {
        "paper_only": True,
        "venue": adapter.venue,
        "cost_assumptions": {
            "fee_bps": costs.fee_bps,
            "slippage_bps": costs.slippage_bps,
            "gas_bps": costs.gas_bps,
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
            }
            for quote in quotes
        ],
        "opportunities": [
            {
                "route": [f"{edge.src.key}->{edge.dst.key}" for edge in item.route],
                "verdict": item.result.verdict.value,
                "gross_edge": item.result.gross_edge,
                "net_edge": item.result.net_edge,
                "risk_adjusted_edge": item.result.risk_adjusted_edge,
                "success_probability": item.result.success_probability,
                "reasons": list(item.result.reasons),
            }
            for item in opportunities
        ],
    }
    print(json.dumps(output, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
