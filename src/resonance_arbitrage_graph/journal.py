from __future__ import annotations

import json
import os
from pathlib import Path

from .evidence import EvidenceReceipt
from .observation import OpportunityObservation, verify_observation_evidence_binding


class JournalError(ValueError):
    pass


def validate_observation_sequence(
    observations: list[OpportunityObservation],
) -> None:
    seen_execution_ids: set[str] = set()
    latest_by_operation: dict[str, OpportunityObservation] = {}

    for observation in observations:
        if observation.execution_id in seen_execution_ids:
            raise JournalError("duplicate execution_id")
        seen_execution_ids.add(observation.execution_id)

        latest = latest_by_operation.get(observation.logical_operation_id)
        if latest is None:
            if observation.attempt != 1:
                raise JournalError("first attempt must be 1")
        else:
            if latest.outcome_class.terminal:
                raise JournalError("logical operation already has a terminal outcome")
            if observation.attempt != latest.attempt + 1:
                raise JournalError("attempt must increment by exactly one")
            if observation.opportunity_id != latest.opportunity_id:
                raise JournalError("retry changed opportunity_id")
            if observation.route_id != latest.route_id:
                raise JournalError("retry changed route_id")
            if observation.detected_at_ms != latest.detected_at_ms:
                raise JournalError("retry changed detected_at_ms")

        latest_by_operation[observation.logical_operation_id] = observation


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

        validate_observation_sequence(observations)
        return observations

    def append(
        self,
        observation: OpportunityObservation,
        *,
        receipt: EvidenceReceipt,
    ) -> None:
        try:
            verify_observation_evidence_binding(observation, receipt)
        except ValueError as exc:
            raise JournalError(f"evidence binding failed: {exc}") from exc

        existing = self.load()
        validate_observation_sequence([*existing, observation])

        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(observation.canonical_json())
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())


def collapse_operations(
    observations: list[OpportunityObservation],
) -> list[OpportunityObservation]:
    validate_observation_sequence(observations)
    latest: dict[str, OpportunityObservation] = {}
    for observation in observations:
        latest[observation.logical_operation_id] = observation
    return [latest[key] for key in sorted(latest)]
