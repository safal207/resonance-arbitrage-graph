from __future__ import annotations

import json
import os
from pathlib import Path

from .observation import OpportunityObservation


class JournalError(ValueError):
    pass


class ObservationJournal:
    """Single-writer append-only JSONL journal for causal opportunity outcomes."""

    def __init__(self, path: str | Path):
        self.path = Path(path)

    def load(self) -> list[OpportunityObservation]:
        if not self.path.exists():
            return []

        observations: list[OpportunityObservation] = []
        with self.path.open("r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                raw = line.strip()
                if not raw:
                    continue
                try:
                    payload = json.loads(raw)
                    if not isinstance(payload, dict):
                        raise ValueError("journal row must be an object")
                    observations.append(OpportunityObservation.from_dict(payload))
                except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
                    raise JournalError(f"invalid journal row {line_number}: {exc}") from exc
        return observations

    def append(self, observation: OpportunityObservation) -> None:
        existing = self.load()

        if any(item.execution_id == observation.execution_id for item in existing):
            raise JournalError("duplicate execution_id")

        same_operation = [
            item
            for item in existing
            if item.logical_operation_id == observation.logical_operation_id
        ]

        if same_operation:
            if any(item.outcome_class.terminal for item in same_operation):
                raise JournalError("logical operation already has a terminal outcome")

            latest = max(same_operation, key=lambda item: item.attempt)
            if observation.attempt != latest.attempt + 1:
                raise JournalError("attempt must increment by exactly one")
            if observation.opportunity_id != latest.opportunity_id:
                raise JournalError("retry changed opportunity_id")
            if observation.route_id != latest.route_id:
                raise JournalError("retry changed route_id")
            if observation.detected_at_ms != latest.detected_at_ms:
                raise JournalError("retry changed detected_at_ms")
        elif observation.attempt != 1:
            raise JournalError("first attempt must be 1")

        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(observation.canonical_json())
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())


def collapse_operations(
    observations: list[OpportunityObservation],
) -> list[OpportunityObservation]:
    latest: dict[str, OpportunityObservation] = {}
    for observation in observations:
        current = latest.get(observation.logical_operation_id)
        if current is None or observation.attempt > current.attempt:
            latest[observation.logical_operation_id] = observation
    return [latest[key] for key in sorted(latest)]
