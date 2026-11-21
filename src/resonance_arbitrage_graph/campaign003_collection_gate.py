"""Fail-closed, finite pre-capture gate for Campaign 003.

Does NOT fetch market data or place an order. A gate check never modifies
the corpus, and a declined slot must not be silently replayed or backfilled.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import os
from pathlib import Path

from .real_market_corpus import load_corpus
from .temporal_holdout import DAYS, START, SLOTS_UTC, extract_holdout

PLANNED_CASES_PER_SLOT = 10
PLANNED_SLOTS = DAYS * len(SLOTS_UTC)
MAX_OPERATIONS = PLANNED_CASES_PER_SLOT * PLANNED_SLOTS
START_MINUTE = 12
LAST_START_MINUTE = 30


@dataclass(frozen=True, slots=True)
class SlotDecision:
    status: str
    date_utc: str
    hour_utc: int
    previous_cases: int

    @property
    def may_collect(self) -> bool:
        return self.status == "ELIGIBLE"


def classify_capture(
    *,
    now_utc: datetime,
    existing_decision_times_ms: tuple[int, ...],
) -> SlotDecision:
    """Reject outside window, duplicates, overflow and future/poisoned samples.

    Decisions are tracked by the source evaluation time and not by a cron
    event's planned time. Never resample a slot with even one partial case.
    """
    if now_utc.tzinfo is None:
        raise ValueError("capture clock must be timezone-aware")
    now = now_utc.astimezone(timezone.utc)
    previous = len(existing_decision_times_ms)
    day_start = START
    day_end = START + timedelta(days=DAYS)
    seen: dict[tuple[str, int], int] = {}
    for time_ms in existing_decision_times_ms:
        if not isinstance(time_ms, int) or isinstance(time_ms, bool) or time_ms < 0:
            raise ValueError("invalid preexisting decision time")
        stamp = datetime.fromtimestamp(time_ms / 1000.0, timezone.utc)
        if not day_start <= stamp.date() < day_end or stamp.hour not in SLOTS_UTC:
            raise ValueError("unexpected historical/off-window operation in Campaign 003")
        key = (stamp.date().isoformat(), stamp.hour)
        seen[key] = seen.get(key, 0) + 1
        if seen[key] > PLANNED_CASES_PER_SLOT:
            raise ValueError("slot exceeds preregistered ten-case ceiling")
        if stamp > now:
            raise ValueError("corpus contains a decision from the future")

    key = (now.date().isoformat(), now.hour)
    if not day_start <= now.date() < day_end or now.hour not in SLOTS_UTC:
        status = "OUT_OF_WINDOW"
    elif now.minute < START_MINUTE or now.minute > LAST_START_MINUTE:
        status = "TOO_EARLY_OR_LATE"
    elif previous >= MAX_OPERATIONS:
        status = "BUDGET_EXHAUSTED"
    elif seen.get(key, 0) != 0:
        status = "ALREADY_STARTED"
    else:
        status = "ELIGIBLE"
    return SlotDecision(status, now.date().isoformat(), now.hour, previous)


def _decision_times(path: Path) -> tuple[int, ...]:
    corpus = load_corpus(path)
    if not corpus.records:
        return ()
    # This validates all prior market/amount/cost/route fields against the
    # preregistration. Fail rather than continuing through pending outcomes.
    extract_holdout(corpus)
    return tuple(
        case.evaluation_time_ms
        for case in corpus.to_replay_bundle().collapsed_cases()
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check future Campaign 003 slot")
    parser.add_argument("--corpus", type=Path, required=True)
    parser.add_argument("--github-output", type=Path)
    args = parser.parse_args(argv)
    decision = classify_capture(
        now_utc=datetime.now(timezone.utc),
        existing_decision_times_ms=_decision_times(args.corpus),
    )
    if args.github_output:
        with args.github_output.open("a", encoding="utf-8") as target:
            target.write("collect=" + ("true" if decision.may_collect else "false") + "\n")
            target.write("status=" + decision.status + "\n")
            target.write("before=" + str(decision.previous_cases) + "\n")
    print(f"Campaign 003 gate: {decision.status} at "
          f"{decision.date_utc} UTC{decision.hour_utc:02d}, "
          f"existing={decision.previous_cases}; max={MAX_OPERATIONS}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
