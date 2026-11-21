"""Pre-registered, non-trading temporal holdout for Campaign 003.

This module never fetches market data, changes policy, or submits an order.
Its decision rule is frozen before any Campaign 003 evidence is collected.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from itertools import product
from math import comb
from pathlib import Path
import argparse
import json

from .opportunity_funnel import _build_row
from .real_market_corpus import RealMarketReplayCorpus, load_corpus

START = date(2026, 11, 24)
DAYS = 28
SLOTS_UTC = (1, 16)
ASSETS = ("ADA", "ETH", "LTC", "SOL", "XRP")
DIRECTIONS = ("via_BTC", "via_asset")
MIN_COMPLETE_PAIRED_DAYS = 24
MIN_ABSOLUTE_UPLIFT = 0.10
MAX_TWO_SIDED_P = 0.05
OLD_CAMPAIGN_SHA = "14a34de29987a2e9a70fe115a63c0411fdf6c8cb7027b02d84c540ebcc6cc614"
EXPECTED_VENUE = "KRAKEN_SPOT"
EXPECTED_AMOUNT_USD = 25.0
EXPECTED_COST_BPS = (10.0, 2.0, 0.0)
EXPECTED_EXECUTE_NET_EDGE = 0.0005
_EXPECTED_PAIRS = set(product(ASSETS, DIRECTIONS))


@dataclass(frozen=True, slots=True)
class HoldoutObservation:
    date_utc: date
    hour_utc: int
    asset: str
    direction: str
    gross_positive: bool
    net_positive: bool = False


def _sign_test(wins: int, losses: int) -> float:
    """Exact two-sided paired-day sign test, excluding tied days."""
    n = wins + losses
    if n == 0:
        return 1.0
    tail = sum(comb(n, k) for k in range(min(wins, losses) + 1))
    return min(1.0, 2.0 * tail / (2 ** n))


def assess_observations(records: list[HoldoutObservation]) -> dict:
    """Every planned day and slot stays in the denominator/coverage report."""
    seen: dict[tuple[date, int, str, str], HoldoutObservation] = {}
    end = START + timedelta(days=DAYS)
    for row in records:
        if not isinstance(row, HoldoutObservation):
            raise ValueError("holdout observations must be typed")
        if not START <= row.date_utc < end:
            raise ValueError("observation outside pre-registered future dates")
        if row.hour_utc not in SLOTS_UTC:
            raise ValueError("observation outside pre-registered UTC slots")
        if (row.asset, row.direction) not in _EXPECTED_PAIRS:
            raise ValueError("unregistered market or direction")
        if type(row.gross_positive) is not bool or type(row.net_positive) is not bool:
            raise ValueError("positive flags must be boolean")
        if row.net_positive and not row.gross_positive:
            raise ValueError("net-positive cannot bypass gross-positive gate")
        key = (row.date_utc, row.hour_utc, row.asset, row.direction)
        if key in seen:
            raise ValueError("duplicate day/slot/market/direction")
        seen[key] = row

    daily = []
    matched = []
    incomplete = []
    for i in range(DAYS):
        day = START + timedelta(days=i)
        by_slot = {}
        for hour in SLOTS_UTC:
            bucket = [row for (d, h, _, _), row in seen.items() if d == day and h == hour]
            by_slot[hour] = bucket
        complete = all(len(by_slot[hour]) == len(_EXPECTED_PAIRS) for hour in SLOTS_UTC)
        summary = {
            "date_utc": day.isoformat(),
            "observed_01": len(by_slot[1]),
            "gross_positive_01": sum(r.gross_positive for r in by_slot[1]),
            "observed_16": len(by_slot[16]),
            "gross_positive_16": sum(r.gross_positive for r in by_slot[16]),
            "complete_pair": complete,
        }
        daily.append(summary)
        if complete:
            matched.append(summary)
        else:
            incomplete.append(day.isoformat())

    n = len(matched) * len(_EXPECTED_PAIRS)
    pos_01 = sum(day["gross_positive_01"] for day in matched)
    pos_16 = sum(day["gross_positive_16"] for day in matched)
    wins = sum(day["gross_positive_16"] > day["gross_positive_01"] for day in matched)
    losses = sum(day["gross_positive_16"] < day["gross_positive_01"] for day in matched)
    ties = len(matched) - wins - losses
    rate_01 = pos_01 / n if n else None
    rate_16 = pos_16 / n if n else None
    delta = (rate_16 - rate_01) if n else None
    p = _sign_test(wins, losses)
    sufficient = len(matched) >= MIN_COMPLETE_PAIRED_DAYS
    replicated = (
        sufficient and delta is not None
        and delta >= MIN_ABSOLUTE_UPLIFT
        and wins > losses
        and p <= MAX_TWO_SIDED_P
    )
    status = (
        "INCONCLUSIVE_COVERAGE" if not sufficient
        else "REPLICATED_GROSS_PATTERN" if replicated
        else "NOT_REPLICATED"
    )
    return {
        "schema": "resonance.verify.temporal-holdout/v0.1",
        "status": status,
        "diagnostic_only": True,
        "paper_only": True,
        "claim_is_not_causal_or_profitable": True,
        "hypothesis": "gross-positive rate at UTC16 exceeds UTC01",
        "preregistered_start_utc": START.isoformat(),
        "preregistered_days": DAYS,
        "slots_utc": list(SLOTS_UTC),
        "minimum_complete_paired_days": MIN_COMPLETE_PAIRED_DAYS,
        "minimum_absolute_uplift": MIN_ABSOLUTE_UPLIFT,
        "maximum_two_sided_p": MAX_TWO_SIDED_P,
        "all_observations": len(seen),
        "complete_paired_days": len(matched),
        "incomplete_paired_days": incomplete,
        "paired_cycles_per_arm": n,
        "gross_positive_01": pos_01,
        "gross_positive_16": pos_16,
        "rate_01": rate_01,
        "rate_16": rate_16,
        "difference_16_minus_01": delta,
        "paired_day_wins_16": wins,
        "paired_day_losses_16": losses,
        "paired_day_ties": ties,
        "paired_day_two_sided_sign_p": p,
        "net_positive_any_observed": sum(row.net_positive for row in seen.values()),
        "daily": daily,
    }


def extract_holdout(corpus: RealMarketReplayCorpus) -> list[HoldoutObservation]:
    """Fail closed on changed market universe, cost assumptions, or nonterminal rows."""
    if corpus.sha256 == OLD_CAMPAIGN_SHA:
        raise ValueError("Campaign 002 cannot be reused as independent evidence")
    output = []
    for case in corpus.to_replay_bundle().collapsed_cases():
        if not case.outcome.terminal:
            raise ValueError("holdout contains unresolved outcome")
        if case.start_amount != EXPECTED_AMOUNT_USD:
            raise ValueError("changed paper capital")
        if abs(case.engine_policy.execute_net_edge - EXPECTED_EXECUTE_NET_EDGE) > 1e-12:
            raise ValueError("changed execute threshold")
        if case.engine_policy.max_quote_age_ms != 3000:
            raise ValueError("changed quote-age policy")
        if len(case.legs) != 3:
            raise ValueError("holdout route must have exactly three legs")
        if any(
            (leg.costs.fee_bps, leg.costs.slippage_bps, leg.costs.gas_bps) != EXPECTED_COST_BPS
            for leg in case.legs
        ):
            raise ValueError("changed modeled costs")
        edges = case.build_route()
        if any(edge.src.venue != EXPECTED_VENUE or edge.dst.venue != EXPECTED_VENUE for edge in edges):
            raise ValueError("different venue")
        path = [edges[0].src.asset] + [edge.dst.asset for edge in edges]
        if path[0] != "USD" or path[-1] != "USD" or "BTC" not in path:
            raise ValueError("not a USD triangular route")
        alt = set(path) - {"USD", "BTC"}
        if len(alt) != 1 or next(iter(alt)) not in ASSETS:
            raise ValueError("market is outside the frozen universe")
        direction = "via_BTC" if path[1] == "BTC" else "via_asset"
        expected = ["USD", "BTC", next(iter(alt)), "USD"] if direction == "via_BTC" else ["USD", next(iter(alt)), "BTC", "USD"]
        if path != expected:
            raise ValueError("unexpected leg ordering")
        ts = datetime.fromtimestamp(case.evaluation_time_ms / 1000, tz=timezone.utc)
        row = _build_row(case)
        output.append(HoldoutObservation(
            date_utc=ts.date(),
            hour_utc=ts.hour,
            asset=next(iter(alt)),
            direction=direction,
            gross_positive=row.gross_positive,
            net_positive=row.net_positive,
        ))
    return output


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Score pre-registered, future-only paper-market holdout")
    parser.add_argument("corpus", type=Path, help="separate verified Campaign 003 real-market corpus")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    if not args.corpus.is_file():
        parser.error("Campaign 003 corpus does not exist; historical data cannot substitute")
    corpus = load_corpus(args.corpus)
    result = assess_observations(extract_holdout(corpus))
    result["corpus_sha256"] = corpus.sha256
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"{result['status']}: {result['complete_paired_days']} complete day pairs, "
          f"delta={result['difference_16_minus_01']}, p={result['paired_day_two_sided_sign_p']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
