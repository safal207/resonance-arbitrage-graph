from __future__ import annotations

from dataclasses import dataclass
from statistics import mean

from .journal import collapse_operations
from .observation import OpportunityObservation, OutcomeClass


@dataclass(frozen=True, slots=True)
class ObservationMetrics:
    logical_operations: int
    true_positive: int
    false_positive: int
    expired: int
    rejected: int
    indeterminate: int
    opportunity_truth_rate: float | None
    false_opportunity_rate: float | None
    route_survival_rate: float | None
    mean_prediction_error_bps: float | None


def calculate_metrics(
    observations: list[OpportunityObservation],
) -> ObservationMetrics:
    rows = collapse_operations(observations)
    counts = {outcome: 0 for outcome in OutcomeClass}
    errors: list[float] = []

    for observation in rows:
        counts[observation.outcome_class] += 1
        error = observation.prediction_error_bps
        if error is not None and observation.outcome_class in {
            OutcomeClass.TRUE_POSITIVE,
            OutcomeClass.FALSE_POSITIVE,
        }:
            errors.append(error)

    truth_population = (
        counts[OutcomeClass.TRUE_POSITIVE]
        + counts[OutcomeClass.FALSE_POSITIVE]
    )
    survival_population = truth_population + counts[OutcomeClass.EXPIRED]

    return ObservationMetrics(
        logical_operations=len(rows),
        true_positive=counts[OutcomeClass.TRUE_POSITIVE],
        false_positive=counts[OutcomeClass.FALSE_POSITIVE],
        expired=counts[OutcomeClass.EXPIRED],
        rejected=counts[OutcomeClass.REJECTED],
        indeterminate=counts[OutcomeClass.INDETERMINATE],
        opportunity_truth_rate=(
            counts[OutcomeClass.TRUE_POSITIVE] / truth_population
            if truth_population
            else None
        ),
        false_opportunity_rate=(
            counts[OutcomeClass.FALSE_POSITIVE] / truth_population
            if truth_population
            else None
        ),
        route_survival_rate=(
            truth_population / survival_population
            if survival_population
            else None
        ),
        mean_prediction_error_bps=mean(errors) if errors else None,
    )
