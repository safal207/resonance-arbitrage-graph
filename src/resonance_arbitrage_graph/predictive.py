from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass
import hashlib
import json
import math
from statistics import mean
from typing import Any

from .replay import ReplayBundle, ReplayCase, replay_case
from .window_regime import derive_window_regime_context


_DATASET_SCHEMA = "resonance.arbitrage.predictive-dataset/v0.1"


def _canonical_json(payload: Any) -> str:
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def _sha256(payload: Any) -> str:
    return hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()


def _probability(value: float, name: str) -> float:
    if not math.isfinite(value) or not 0.0 <= value <= 1.0:
        raise ValueError(f"{name} must be finite and between 0 and 1")
    return value


@dataclass(frozen=True, slots=True)
class PredictiveFeatures:
    expected_edge_bps: float
    required_edge_bps: float
    route_hops: int
    total_cost_bps: float
    total_latency_ms: int
    min_success_probability: float
    normalized_spread_bps: float
    top_of_book_capacity_ratio: float
    quote_age_ms: int
    quote_age_dispersion_ms: int
    cross_rate_dislocation_bps: float | None
    short_window_return_volatility_bps: float | None

    def __post_init__(self) -> None:
        finite_non_negative = (
            "required_edge_bps",
            "total_cost_bps",
            "normalized_spread_bps",
            "top_of_book_capacity_ratio",
        )
        if not math.isfinite(self.expected_edge_bps):
            raise ValueError("expected_edge_bps must be finite")
        for name in finite_non_negative:
            value = getattr(self, name)
            if not math.isfinite(value) or value < 0:
                raise ValueError(f"{name} must be finite and non-negative")
        if self.top_of_book_capacity_ratio <= 0:
            raise ValueError("top_of_book_capacity_ratio must be positive")
        if self.route_hops < 1:
            raise ValueError("route_hops must be >= 1")
        if self.total_latency_ms < 0 or self.quote_age_ms < 0 or self.quote_age_dispersion_ms < 0:
            raise ValueError("latency and quote ages must be non-negative")
        _probability(self.min_success_probability, "min_success_probability")
        for name in ("cross_rate_dislocation_bps", "short_window_return_volatility_bps"):
            value = getattr(self, name)
            if value is not None and (not math.isfinite(value) or value < 0):
                raise ValueError(f"{name} must be finite and non-negative when supplied")

    def to_payload(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class PredictiveTargets:
    target_available_at_ms: int | None
    realized_net_edge_bps: float | None
    survived: bool | None
    positive_edge: bool | None
    met_required_edge: bool | None

    def __post_init__(self) -> None:
        if self.target_available_at_ms is not None and self.target_available_at_ms < 0:
            raise ValueError("target_available_at_ms must be non-negative")
        if self.realized_net_edge_bps is not None and not math.isfinite(self.realized_net_edge_bps):
            raise ValueError("realized_net_edge_bps must be finite when supplied")
        flags = (self.survived, self.positive_edge, self.met_required_edge)
        if any(flag is not None and not isinstance(flag, bool) for flag in flags):
            raise ValueError("predictive target flags must be bool or None")
        if self.target_available_at_ms is None:
            if self.realized_net_edge_bps is not None or any(flag is not None for flag in flags):
                raise ValueError("unavailable target cannot carry labels")
            return
        if self.survived is None or self.positive_edge is None or self.met_required_edge is None:
            raise ValueError("available target must carry all labels")
        if self.survived and self.realized_net_edge_bps is None:
            raise ValueError("survived target requires realized edge")
        if not self.survived and self.realized_net_edge_bps is not None:
            raise ValueError("expired target cannot carry realized edge")
        if not self.survived and (self.positive_edge or self.met_required_edge):
            raise ValueError("expired target cannot be positive or meet required edge")

    @property
    def available(self) -> bool:
        return self.target_available_at_ms is not None

    def to_payload(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class PredictiveRow:
    case_id: str
    logical_operation_id: str
    route_id: str
    decision_at_ms: int
    start_amount: float
    regime: str
    case_sha256: str
    features: PredictiveFeatures
    targets: PredictiveTargets

    def __post_init__(self) -> None:
        for name in ("case_id", "logical_operation_id", "route_id", "regime", "case_sha256"):
            if not getattr(self, name):
                raise ValueError(f"{name} must be non-empty")
        if self.decision_at_ms < 0:
            raise ValueError("decision_at_ms must be non-negative")
        if not math.isfinite(self.start_amount) or self.start_amount <= 0:
            raise ValueError("start_amount must be finite and positive")
        if self.targets.target_available_at_ms is not None and self.targets.target_available_at_ms < self.decision_at_ms:
            raise ValueError("target cannot be available before the decision")

    def to_payload(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "logical_operation_id": self.logical_operation_id,
            "route_id": self.route_id,
            "decision_at_ms": self.decision_at_ms,
            "start_amount": self.start_amount,
            "regime": self.regime,
            "case_sha256": self.case_sha256,
            "features": self.features.to_payload(),
            "targets": self.targets.to_payload(),
        }

    @property
    def sha256(self) -> str:
        return _sha256(self.to_payload())


def build_predictive_row(case: ReplayCase) -> PredictiveRow:
    result = replay_case(case)
    route = case.build_route()
    context = derive_window_regime_context(
        route,
        case.snapshots,
        windows_by_market=case.windows_by_market,
        evaluation_time_ms=case.evaluation_time_ms,
        start_amount=case.start_amount,
        regime_policy=case.regime_policy,
    )
    regime_features = context.classification.features

    features = PredictiveFeatures(
        expected_edge_bps=result.expected_edge_bps,
        required_edge_bps=result.required_edge_bps,
        route_hops=len(route),
        total_cost_bps=sum(edge.total_cost_bps for edge in route),
        total_latency_ms=sum(edge.latency_ms for edge in route),
        min_success_probability=min(edge.success_probability for edge in route),
        normalized_spread_bps=regime_features.normalized_spread_bps,
        top_of_book_capacity_ratio=regime_features.top_of_book_capacity_ratio,
        quote_age_ms=regime_features.quote_age_ms,
        quote_age_dispersion_ms=regime_features.quote_age_dispersion_ms,
        cross_rate_dislocation_bps=regime_features.cross_rate_dislocation_bps,
        short_window_return_volatility_bps=regime_features.short_window_return_volatility_bps,
    )

    outcome = case.outcome
    if outcome.realized_net_edge_bps is not None:
        targets = PredictiveTargets(
            target_available_at_ms=outcome.observed_at_ms,
            realized_net_edge_bps=outcome.realized_net_edge_bps,
            survived=True,
            positive_edge=outcome.realized_net_edge_bps > 0.0,
            met_required_edge=outcome.realized_net_edge_bps >= result.required_edge_bps,
        )
    elif outcome.expired:
        targets = PredictiveTargets(
            target_available_at_ms=outcome.observed_at_ms,
            realized_net_edge_bps=None,
            survived=False,
            positive_edge=False,
            met_required_edge=False,
        )
    else:
        targets = PredictiveTargets(
            target_available_at_ms=None,
            realized_net_edge_bps=None,
            survived=None,
            positive_edge=None,
            met_required_edge=None,
        )

    return PredictiveRow(
        case_id=case.case_id,
        logical_operation_id=case.logical_operation_id,
        route_id=case.route_id,
        decision_at_ms=case.evaluation_time_ms,
        start_amount=case.start_amount,
        regime=result.regime.value,
        case_sha256=case.sha256,
        features=features,
        targets=targets,
    )


@dataclass(frozen=True, slots=True)
class PredictiveDataset:
    source_bundle_sha256: str
    rows: tuple[PredictiveRow, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "rows", tuple(self.rows))
        if not self.source_bundle_sha256:
            raise ValueError("source_bundle_sha256 must be non-empty")
        if not self.rows:
            raise ValueError("predictive dataset requires at least one row")
        operation_ids = [row.logical_operation_id for row in self.rows]
        if len(operation_ids) != len(set(operation_ids)):
            raise ValueError("predictive dataset must contain one row per logical operation")
        ordered = sorted(self.rows, key=lambda row: (row.decision_at_ms, row.logical_operation_id))
        if list(self.rows) != ordered:
            raise ValueError("predictive dataset rows must be chronologically ordered")

    def canonical_payload(self) -> dict[str, Any]:
        return {
            "schema": _DATASET_SCHEMA,
            "source_bundle_sha256": self.source_bundle_sha256,
            "rows": [row.to_payload() for row in self.rows],
        }

    @property
    def sha256(self) -> str:
        return _sha256(self.canonical_payload())


def build_predictive_dataset(bundle: ReplayBundle) -> PredictiveDataset:
    rows = tuple(build_predictive_row(case) for case in bundle.collapsed_cases())
    return PredictiveDataset(source_bundle_sha256=bundle.sha256, rows=rows)


@dataclass(frozen=True, slots=True)
class PredictiveSplit:
    training_rows: tuple[PredictiveRow, ...]
    validation_rows: tuple[PredictiveRow, ...]
    excluded_late_target_rows: tuple[PredictiveRow, ...]
    validation_start_ms: int

    def __post_init__(self) -> None:
        if not self.training_rows:
            raise ValueError("predictive split requires at least one training row")
        if not self.validation_rows:
            raise ValueError("predictive split requires at least one validation row")
        if self.validation_start_ms != self.validation_rows[0].decision_at_ms:
            raise ValueError("validation_start_ms must match the first validation decision")
        for row in self.training_rows:
            available_at = row.targets.target_available_at_ms
            if available_at is None or available_at > self.validation_start_ms:
                raise ValueError("training row target was not available before validation")
        if any(row.decision_at_ms >= self.validation_start_ms for row in self.training_rows):
            raise ValueError("training decisions must precede validation")

    def to_payload(self) -> dict[str, Any]:
        return {
            "validation_start_ms": self.validation_start_ms,
            "training_operation_ids": [row.logical_operation_id for row in self.training_rows],
            "validation_operation_ids": [row.logical_operation_id for row in self.validation_rows],
            "excluded_late_target_operation_ids": [
                row.logical_operation_id for row in self.excluded_late_target_rows
            ],
        }


def chronological_predictive_split(
    dataset: PredictiveDataset,
    *,
    validation_fraction: float = 0.30,
) -> PredictiveSplit:
    if not math.isfinite(validation_fraction) or not 0.0 < validation_fraction < 1.0:
        raise ValueError("validation_fraction must be between 0 and 1")
    if len(dataset.rows) < 2:
        raise ValueError("predictive split requires at least two logical operations")

    split_index = int(len(dataset.rows) * (1.0 - validation_fraction))
    split_index = max(1, min(len(dataset.rows) - 1, split_index))
    earlier = dataset.rows[:split_index]
    validation = dataset.rows[split_index:]
    validation_start_ms = validation[0].decision_at_ms

    training: list[PredictiveRow] = []
    excluded: list[PredictiveRow] = []
    for row in earlier:
        available_at = row.targets.target_available_at_ms
        if available_at is not None and available_at <= validation_start_ms:
            training.append(row)
        else:
            excluded.append(row)

    if not training:
        raise ValueError("no leakage-safe training rows are available before validation")
    return PredictiveSplit(
        training_rows=tuple(training),
        validation_rows=tuple(validation),
        excluded_late_target_rows=tuple(excluded),
        validation_start_ms=validation_start_ms,
    )


@dataclass(frozen=True, slots=True)
class PredictivePrediction:
    logical_operation_id: str
    model_id: str
    trained_through_ms: int
    predicted_realized_edge_bps: float
    survival_probability: float
    positive_edge_probability: float

    def __post_init__(self) -> None:
        if not self.logical_operation_id or not self.model_id:
            raise ValueError("prediction identifiers must be non-empty")
        if self.trained_through_ms < 0:
            raise ValueError("trained_through_ms must be non-negative")
        if not math.isfinite(self.predicted_realized_edge_bps):
            raise ValueError("predicted_realized_edge_bps must be finite")
        _probability(self.survival_probability, "survival_probability")
        _probability(self.positive_edge_probability, "positive_edge_probability")


@dataclass(frozen=True, slots=True)
class HistoricalMeanBaseline:
    model_id: str
    trained_through_ms: int
    mean_realized_edge_bps: float
    survival_probability: float
    positive_edge_probability: float

    @classmethod
    def fit(
        cls,
        rows: Sequence[PredictiveRow],
        *,
        model_id: str = "historical-mean/v0.1",
    ) -> "HistoricalMeanBaseline":
        rows = tuple(rows)
        if not rows:
            raise ValueError("baseline requires training rows")
        if not model_id:
            raise ValueError("model_id must be non-empty")

        available = [row for row in rows if row.targets.available]
        if len(available) != len(rows):
            raise ValueError("baseline training rows must have available targets")
        realized_edges = [
            row.targets.realized_net_edge_bps
            for row in rows
            if row.targets.realized_net_edge_bps is not None
        ]
        if not realized_edges:
            raise ValueError("baseline requires at least one realized edge target")
        survival_labels = [1.0 if row.targets.survived else 0.0 for row in rows]
        positive_labels = [1.0 if row.targets.positive_edge else 0.0 for row in rows]
        trained_through_ms = max(
            row.targets.target_available_at_ms or 0
            for row in rows
        )
        return cls(
            model_id=model_id,
            trained_through_ms=trained_through_ms,
            mean_realized_edge_bps=mean(realized_edges),
            survival_probability=mean(survival_labels),
            positive_edge_probability=mean(positive_labels),
        )

    def predict(self, rows: Sequence[PredictiveRow]) -> tuple[PredictivePrediction, ...]:
        predictions: list[PredictivePrediction] = []
        for row in rows:
            if row.decision_at_ms < self.trained_through_ms:
                raise ValueError("prediction decision predates model training horizon")
            predictions.append(
                PredictivePrediction(
                    logical_operation_id=row.logical_operation_id,
                    model_id=self.model_id,
                    trained_through_ms=self.trained_through_ms,
                    predicted_realized_edge_bps=self.mean_realized_edge_bps,
                    survival_probability=self.survival_probability,
                    positive_edge_probability=self.positive_edge_probability,
                )
            )
        return tuple(predictions)


@dataclass(frozen=True, slots=True)
class ShadowEvaluation:
    evaluated_rows: int
    realized_edge_rows: int
    mean_absolute_edge_error_bps: float | None
    survival_brier_score: float | None
    positive_edge_brier_score: float | None
    selected_rows: int
    selected_realized_rows: int
    selected_expired_rows: int
    selected_realized_pnl_units: float

    def to_payload(self) -> dict[str, Any]:
        return asdict(self)


def evaluate_shadow_predictions(
    rows: Sequence[PredictiveRow],
    predictions: Sequence[PredictivePrediction],
    *,
    min_survival_probability: float = 0.50,
    min_positive_edge_probability: float = 0.50,
) -> ShadowEvaluation:
    _probability(min_survival_probability, "min_survival_probability")
    _probability(min_positive_edge_probability, "min_positive_edge_probability")
    rows = tuple(rows)
    predictions = tuple(predictions)
    prediction_by_operation: Mapping[str, PredictivePrediction] = {
        prediction.logical_operation_id: prediction for prediction in predictions
    }
    if len(prediction_by_operation) != len(predictions):
        raise ValueError("duplicate prediction logical_operation_id")

    edge_errors: list[float] = []
    survival_errors: list[float] = []
    positive_errors: list[float] = []
    selected_rows = 0
    selected_realized_rows = 0
    selected_expired_rows = 0
    selected_realized_pnl_units = 0.0
    evaluated_rows = 0
    realized_edge_rows = 0

    for row in rows:
        if not row.targets.available:
            continue
        try:
            prediction = prediction_by_operation[row.logical_operation_id]
        except KeyError as exc:
            raise ValueError("missing prediction for an evaluable row") from exc
        if prediction.trained_through_ms > row.decision_at_ms:
            raise ValueError("prediction used information unavailable at decision time")
        evaluated_rows += 1

        if row.targets.realized_net_edge_bps is not None:
            realized_edge_rows += 1
            edge_errors.append(
                abs(prediction.predicted_realized_edge_bps - row.targets.realized_net_edge_bps)
            )
        survival_label = 1.0 if row.targets.survived else 0.0
        positive_label = 1.0 if row.targets.positive_edge else 0.0
        survival_errors.append((prediction.survival_probability - survival_label) ** 2)
        positive_errors.append((prediction.positive_edge_probability - positive_label) ** 2)

        selected = (
            prediction.predicted_realized_edge_bps > 0.0
            and prediction.survival_probability >= min_survival_probability
            and prediction.positive_edge_probability >= min_positive_edge_probability
        )
        if not selected:
            continue

        selected_rows += 1
        if row.targets.realized_net_edge_bps is not None:
            selected_realized_rows += 1
            selected_realized_pnl_units += (
                row.start_amount * row.targets.realized_net_edge_bps / 10_000.0
            )
        elif row.targets.survived is False:
            selected_expired_rows += 1

    if evaluated_rows == 0:
        raise ValueError("shadow evaluation requires available validation targets")

    return ShadowEvaluation(
        evaluated_rows=evaluated_rows,
        realized_edge_rows=realized_edge_rows,
        mean_absolute_edge_error_bps=mean(edge_errors) if edge_errors else None,
        survival_brier_score=mean(survival_errors) if survival_errors else None,
        positive_edge_brier_score=mean(positive_errors) if positive_errors else None,
        selected_rows=selected_rows,
        selected_realized_rows=selected_realized_rows,
        selected_expired_rows=selected_expired_rows,
        selected_realized_pnl_units=selected_realized_pnl_units,
    )
