from __future__ import annotations

from collections.abc import Sequence
from dataclasses import asdict, dataclass
import hashlib
import json
import math
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from .predictive import (
    HistoricalMeanBaseline,
    OpportunityFeatureVector,
    PredictionTarget,
    PredictiveDataset,
    PredictiveModelArtifact,
    PredictiveOpportunityReceipt,
    PredictivePrediction,
    PredictiveRow,
    PredictiveTrainingManifest,
    ShadowEvaluation,
    build_training_manifest,
    evaluate_shadow_predictions,
    predict_with_historical_baseline,
)

_ENCODER_VERSION = "catboost-tabular/v0.1"

_NUMERIC_FEATURES = (
    "start_amount",
    "expected_edge_bps",
    "required_edge_bps",
    "route_hops",
    "total_cost_bps",
    "total_latency_ms",
    "route_success_probability",
    "normalized_spread_bps",
    "top_of_book_capacity_ratio",
    "quote_age_ms",
    "quote_age_dispersion_ms",
    "cross_rate_dislocation_bps",
    "cross_rate_dislocation_missing",
    "short_window_return_volatility_bps",
    "short_window_return_volatility_missing",
    "min_window_sample_count",
    "min_window_coverage_ratio",
    "same_venue",
)

_CATEGORICAL_FEATURES = (
    "deterministic_verdict",
    "market_regime",
    "route_id",
    "venue_sequence",
    "symbol_sequence",
    "side_sequence",
    "asset_path",
)

_FEATURE_NAMES = _NUMERIC_FEATURES + _CATEGORICAL_FEATURES
_CATEGORICAL_INDICES = tuple(
    range(len(_NUMERIC_FEATURES), len(_NUMERIC_FEATURES) + len(_CATEGORICAL_FEATURES))
)


def _canonical_json(payload: Any) -> str:
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _sha256_json(payload: Any) -> str:
    return _sha256_bytes(_canonical_json(payload).encode("utf-8"))


def _probability(value: float, name: str) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ValueError(f"{name} must be numeric")
    value = float(value)
    if not math.isfinite(value) or not 0.0 <= value <= 1.0:
        raise ValueError(f"{name} must be finite and between 0 and 1")
    return value


@dataclass(frozen=True, slots=True)
class CatBoostResearchConfig:
    iterations: int = 64
    depth: int = 4
    learning_rate: float = 0.05
    l2_leaf_reg: float = 3.0
    random_seed: int = 207
    thread_count: int = 1

    def __post_init__(self) -> None:
        if self.iterations < 1:
            raise ValueError("iterations must be positive")
        if not 1 <= self.depth <= 16:
            raise ValueError("depth must be between 1 and 16")
        for name in ("learning_rate", "l2_leaf_reg"):
            value = getattr(self, name)
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                raise ValueError(f"{name} must be numeric")
            if not math.isfinite(float(value)) or float(value) <= 0:
                raise ValueError(f"{name} must be finite and positive")
        if self.random_seed < 0:
            raise ValueError("random_seed must be non-negative")
        if self.thread_count < 1:
            raise ValueError("thread_count must be positive")

    def to_payload(self) -> dict[str, Any]:
        return asdict(self)


def feature_names() -> tuple[str, ...]:
    return _FEATURE_NAMES


def categorical_feature_indices() -> tuple[int, ...]:
    return _CATEGORICAL_INDICES


def encode_feature_vector(vector: OpportunityFeatureVector) -> tuple[Any, ...]:
    cross_missing = vector.cross_rate_dislocation_bps is None
    volatility_missing = vector.short_window_return_volatility_bps is None
    numeric: tuple[float, ...] = (
        float(vector.start_amount),
        float(vector.expected_edge_bps),
        float(vector.required_edge_bps),
        float(vector.route_hops),
        float(vector.total_cost_bps),
        float(vector.total_latency_ms),
        float(vector.route_success_probability),
        float(vector.normalized_spread_bps),
        float(vector.top_of_book_capacity_ratio),
        float(vector.quote_age_ms),
        float(vector.quote_age_dispersion_ms),
        float(vector.cross_rate_dislocation_bps or 0.0),
        1.0 if cross_missing else 0.0,
        float(vector.short_window_return_volatility_bps or 0.0),
        1.0 if volatility_missing else 0.0,
        float(vector.min_window_sample_count),
        float(vector.min_window_coverage_ratio),
        1.0 if vector.same_venue else 0.0,
    )
    categorical = (
        vector.deterministic_verdict,
        vector.market_regime,
        vector.route_id,
        ">".join(vector.venue_sequence),
        ">".join(vector.symbol_sequence),
        ">".join(vector.side_sequence),
        ">".join(vector.asset_path),
    )
    encoded = numeric + categorical
    if len(encoded) != len(_FEATURE_NAMES):
        raise AssertionError("CatBoost feature encoder shape drifted")
    return encoded


def _matrix(rows: Sequence[PredictiveRow]) -> list[list[Any]]:
    return [list(encode_feature_vector(row.feature_vector)) for row in rows]


def _load_catboost() -> tuple[Any, Any, Any, str]:
    try:
        import catboost
        from catboost import CatBoostClassifier, CatBoostRegressor, Pool
    except ImportError as exc:
        raise RuntimeError(
            'CatBoost research support is optional; install ".[ml-catboost]"'
        ) from exc
    return CatBoostRegressor, CatBoostClassifier, Pool, str(catboost.__version__)


def _common_model_params(config: CatBoostResearchConfig) -> dict[str, Any]:
    return {
        "iterations": config.iterations,
        "depth": config.depth,
        "learning_rate": config.learning_rate,
        "l2_leaf_reg": config.l2_leaf_reg,
        "random_seed": config.random_seed,
        "thread_count": config.thread_count,
        "verbose": False,
        "allow_writing_files": False,
        "random_strength": 0.0,
        "bootstrap_type": "No",
    }


def _model_sha256(model: Any) -> str:
    with TemporaryDirectory(prefix="resonance-catboost-") as directory:
        path = Path(directory) / "model.cbm"
        model.save_model(str(path), format="cbm")
        return _sha256_bytes(path.read_bytes())


@dataclass(frozen=True, slots=True)
class ConstantProbabilityHead:
    probability: float

    def __post_init__(self) -> None:
        _probability(self.probability, "probability")

    @property
    def sha256(self) -> str:
        return _sha256_json(
            {
                "kind": "constant_probability",
                "probability": self.probability,
            }
        )

    def predict_probability(self, _pool: Any) -> float:
        return self.probability


@dataclass(slots=True)
class CatBoostProbabilityHead:
    model: Any
    model_sha256: str

    def predict_probability(self, pool: Any) -> float:
        values = self.model.predict_proba(pool)
        return _probability(float(values[0][1]), "CatBoost probability")


ProbabilityHead = ConstantProbabilityHead | CatBoostProbabilityHead


@dataclass(slots=True)
class CatBoostPredictiveModel:
    manifest: PredictiveTrainingManifest
    artifact: PredictiveModelArtifact
    regressor: Any
    survival_head: ProbabilityHead
    positive_pnl_head: ProbabilityHead

    @property
    def model_id(self) -> str:
        return self.artifact.model_id

    @property
    def trained_through_ms(self) -> int:
        return self.manifest.target_available_through_ms


def _fit_probability_head(
    classifier_type: Any,
    matrix: Sequence[Sequence[Any]],
    labels: Sequence[int],
    *,
    config: CatBoostResearchConfig,
    pool_type: Any,
) -> ProbabilityHead:
    if not labels:
        raise ValueError("probability head requires labels")
    unique = set(labels)
    if not unique <= {0, 1}:
        raise ValueError("probability head labels must be binary")
    if len(unique) == 1:
        return ConstantProbabilityHead(probability=float(labels[0]))

    model = classifier_type(
        loss_function="Logloss",
        **_common_model_params(config),
    )
    pool = pool_type(
        data=[list(row) for row in matrix],
        label=list(labels),
        cat_features=list(_CATEGORICAL_INDICES),
        feature_names=list(_FEATURE_NAMES),
    )
    model.fit(pool)
    return CatBoostProbabilityHead(model=model, model_sha256=_model_sha256(model))


def _head_identity(head: ProbabilityHead) -> dict[str, Any]:
    if isinstance(head, ConstantProbabilityHead):
        return {
            "kind": "constant_probability",
            "sha256": head.sha256,
            "probability": head.probability,
        }
    return {
        "kind": "catboost_classifier",
        "sha256": head.model_sha256,
    }


def fit_catboost_predictive_model(
    rows: Sequence[PredictiveRow],
    *,
    config: CatBoostResearchConfig | None = None,
) -> CatBoostPredictiveModel:
    rows = tuple(rows)
    if len(rows) < 2:
        raise ValueError("CatBoost research model requires at least two training rows")
    if any(not row.targets.available for row in rows):
        raise ValueError("CatBoost training only accepts rows with available targets")
    config = config or CatBoostResearchConfig()
    regressor_type, classifier_type, pool_type, catboost_version = _load_catboost()

    manifest = build_training_manifest(
        rows,
        model_family="catboost_multihead",
        model_config={
            "adapter_version": _ENCODER_VERSION,
            "catboost_version": catboost_version,
            "feature_names": list(_FEATURE_NAMES),
            "categorical_feature_indices": list(_CATEGORICAL_INDICES),
            "config": config.to_payload(),
        },
    )

    realized_rows = tuple(
        row for row in rows if row.targets.future_net_edge_bps is not None
    )
    if len(realized_rows) < 2:
        raise ValueError(
            "CatBoost edge regressor requires at least two realized-edge training rows"
        )
    regressor = regressor_type(
        loss_function="RMSE",
        **_common_model_params(config),
    )
    regression_pool = pool_type(
        data=_matrix(realized_rows),
        label=[float(row.targets.future_net_edge_bps) for row in realized_rows],
        cat_features=list(_CATEGORICAL_INDICES),
        feature_names=list(_FEATURE_NAMES),
    )
    regressor.fit(regression_pool)
    regressor_sha256 = _model_sha256(regressor)

    all_matrix = _matrix(rows)
    survival_head = _fit_probability_head(
        classifier_type,
        all_matrix,
        [1 if row.targets.survived else 0 for row in rows],
        config=config,
        pool_type=pool_type,
    )
    positive_pnl_head = _fit_probability_head(
        classifier_type,
        all_matrix,
        [1 if row.targets.positive_realized_pnl else 0 for row in rows],
        config=config,
        pool_type=pool_type,
    )

    artifact = PredictiveModelArtifact(
        model_family="catboost_multihead",
        training_manifest_sha256=manifest.sha256,
        parameters={
            "adapter_version": _ENCODER_VERSION,
            "catboost_version": catboost_version,
            "regressor_sha256": regressor_sha256,
            "survival_head": _head_identity(survival_head),
            "positive_pnl_head": _head_identity(positive_pnl_head),
        },
    )
    return CatBoostPredictiveModel(
        manifest=manifest,
        artifact=artifact,
        regressor=regressor,
        survival_head=survival_head,
        positive_pnl_head=positive_pnl_head,
    )


def _prediction_receipt(
    row: PredictiveRow,
    model: CatBoostPredictiveModel,
    *,
    target: PredictionTarget,
    value: float,
) -> PredictiveOpportunityReceipt:
    if model.trained_through_ms > row.decision_at_ms:
        raise ValueError("model training used targets unavailable at prediction time")
    vector = row.feature_vector
    feature_schema = vector.canonical_payload()["schema"]
    return PredictiveOpportunityReceipt(
        logical_operation_id=row.logical_operation_id,
        decision_timestamp_ms=row.decision_at_ms,
        feature_schema_version=feature_schema,
        feature_vector_sha256=vector.sha256,
        model_id=model.model_id,
        model_artifact_sha256=model.artifact.sha256,
        training_manifest_sha256=model.manifest.sha256,
        prediction_target=target,
        prediction_value=value,
        prediction_timestamp_ms=row.decision_at_ms,
        policy_context_sha256=vector.policy_context_sha256,
        source_replay_case_sha256=vector.source_replay_case_sha256,
    )


def predict_with_catboost(
    model: CatBoostPredictiveModel,
    rows: Sequence[PredictiveRow],
) -> tuple[PredictivePrediction, ...]:
    predictions: list[PredictivePrediction] = []
    for row in rows:
        if model.trained_through_ms > row.decision_at_ms:
            raise ValueError("CatBoost model training horizon exceeds prediction time")
        encoded = encode_feature_vector(row.feature_vector)
        _, _, pool_type, _ = _load_catboost()
        prediction_pool = pool_type(
            data=[list(encoded)],
            cat_features=list(_CATEGORICAL_INDICES),
            feature_names=list(_FEATURE_NAMES),
        )
        predicted_edge = float(model.regressor.predict(prediction_pool)[0])
        if not math.isfinite(predicted_edge):
            raise ValueError("CatBoost edge prediction must be finite")
        survival_probability = model.survival_head.predict_probability(prediction_pool)
        positive_probability = model.positive_pnl_head.predict_probability(prediction_pool)

        values = (
            (PredictionTarget.FUTURE_NET_EDGE_BPS, predicted_edge),
            (PredictionTarget.SURVIVAL_PROBABILITY, survival_probability),
            (
                PredictionTarget.POSITIVE_REALIZED_PNL_PROBABILITY,
                positive_probability,
            ),
        )
        receipts = tuple(
            _prediction_receipt(row, model, target=target, value=value)
            for target, value in values
        )
        predictions.append(
            PredictivePrediction(
                logical_operation_id=row.logical_operation_id,
                model_id=model.model_id,
                predicted_future_net_edge_bps=predicted_edge,
                survival_probability=survival_probability,
                positive_realized_pnl_probability=positive_probability,
                receipts=receipts,
            )
        )
    return tuple(predictions)


@dataclass(frozen=True, slots=True)
class CatBoostWalkForwardComparison:
    min_training_rows: int
    successful_fold_count: int
    skipped_fold_count: int
    validation_operation_ids: tuple[str, ...]
    skipped_validation_operation_ids: tuple[str, ...]
    excluded_late_target_operation_ids: tuple[str, ...]
    historical_mean: ShadowEvaluation
    catboost: ShadowEvaluation
    selected_pnl_delta_units: float
    edge_mae_delta_bps: float | None
    survival_brier_delta: float | None
    positive_pnl_brier_delta: float | None
    paper_only: bool = True

    def __post_init__(self) -> None:
        if self.min_training_rows < 2:
            raise ValueError("min_training_rows must be at least two")
        if self.successful_fold_count != len(self.validation_operation_ids):
            raise ValueError("successful fold count does not match validation IDs")
        if self.skipped_fold_count != len(self.skipped_validation_operation_ids):
            raise ValueError("skipped fold count does not match skipped validation IDs")
        if self.paper_only is not True:
            raise ValueError("walk-forward comparison must remain paper-only")

    def to_payload(self) -> dict[str, Any]:
        return {
            "schema": "resonance.arbitrage.catboost-walk-forward/v0.1",
            "min_training_rows": self.min_training_rows,
            "successful_fold_count": self.successful_fold_count,
            "skipped_fold_count": self.skipped_fold_count,
            "validation_operation_ids": list(self.validation_operation_ids),
            "skipped_validation_operation_ids": list(
                self.skipped_validation_operation_ids
            ),
            "excluded_late_target_operation_ids": list(
                self.excluded_late_target_operation_ids
            ),
            "historical_mean": self.historical_mean.to_payload(),
            "catboost": self.catboost.to_payload(),
            "selected_pnl_delta_units": self.selected_pnl_delta_units,
            "edge_mae_delta_bps": self.edge_mae_delta_bps,
            "survival_brier_delta": self.survival_brier_delta,
            "positive_pnl_brier_delta": self.positive_pnl_brier_delta,
            "paper_only": self.paper_only,
        }

    @property
    def sha256(self) -> str:
        return _sha256_json(self.to_payload())


def _optional_delta(left: float | None, right: float | None) -> float | None:
    if left is None or right is None:
        return None
    return left - right


def run_catboost_walk_forward(
    dataset: PredictiveDataset,
    *,
    config: CatBoostResearchConfig | None = None,
    min_training_rows: int = 5,
    min_survival_probability: float = 0.50,
    min_positive_realized_pnl_probability: float = 0.50,
) -> CatBoostWalkForwardComparison:
    if min_training_rows < 2:
        raise ValueError("min_training_rows must be at least two")
    if len(dataset.rows) <= min_training_rows:
        raise ValueError("dataset is too small for requested walk-forward training")
    config = config or CatBoostResearchConfig()

    evaluation_rows: list[PredictiveRow] = []
    baseline_predictions: list[PredictivePrediction] = []
    catboost_predictions: list[PredictivePrediction] = []
    skipped_validation_ids: list[str] = []
    excluded_late_ids: list[str] = []

    for validation_index in range(min_training_rows, len(dataset.rows)):
        validation_row = dataset.rows[validation_index]
        if not validation_row.targets.available:
            skipped_validation_ids.append(validation_row.logical_operation_id)
            continue

        training: list[PredictiveRow] = []
        for row in dataset.rows[:validation_index]:
            available_at = row.targets.target_available_at_ms
            if available_at is not None and available_at <= validation_row.decision_at_ms:
                training.append(row)
            else:
                excluded_late_ids.append(row.logical_operation_id)

        realized_training_rows = sum(
            row.targets.future_net_edge_bps is not None for row in training
        )
        if len(training) < min_training_rows or realized_training_rows < 2:
            skipped_validation_ids.append(validation_row.logical_operation_id)
            continue

        baseline = HistoricalMeanBaseline.fit(training)
        catboost_model = fit_catboost_predictive_model(training, config=config)
        baseline_prediction = predict_with_historical_baseline(
            baseline, (validation_row,)
        )[0]
        catboost_prediction = predict_with_catboost(
            catboost_model, (validation_row,)
        )[0]

        evaluation_rows.append(validation_row)
        baseline_predictions.append(baseline_prediction)
        catboost_predictions.append(catboost_prediction)

    if not evaluation_rows:
        raise ValueError("walk-forward produced no evaluable leakage-safe folds")

    baseline_evaluation = evaluate_shadow_predictions(
        evaluation_rows,
        baseline_predictions,
        min_survival_probability=min_survival_probability,
        min_positive_realized_pnl_probability=min_positive_realized_pnl_probability,
    )
    catboost_evaluation = evaluate_shadow_predictions(
        evaluation_rows,
        catboost_predictions,
        min_survival_probability=min_survival_probability,
        min_positive_realized_pnl_probability=min_positive_realized_pnl_probability,
    )

    excluded_unique = tuple(dict.fromkeys(excluded_late_ids))
    return CatBoostWalkForwardComparison(
        min_training_rows=min_training_rows,
        successful_fold_count=len(evaluation_rows),
        skipped_fold_count=len(skipped_validation_ids),
        validation_operation_ids=tuple(
            row.logical_operation_id for row in evaluation_rows
        ),
        skipped_validation_operation_ids=tuple(skipped_validation_ids),
        excluded_late_target_operation_ids=excluded_unique,
        historical_mean=baseline_evaluation,
        catboost=catboost_evaluation,
        selected_pnl_delta_units=(
            catboost_evaluation.selected_realized_pnl_units
            - baseline_evaluation.selected_realized_pnl_units
        ),
        edge_mae_delta_bps=_optional_delta(
            catboost_evaluation.mean_absolute_edge_error_bps,
            baseline_evaluation.mean_absolute_edge_error_bps,
        ),
        survival_brier_delta=_optional_delta(
            catboost_evaluation.survival_brier_score,
            baseline_evaluation.survival_brier_score,
        ),
        positive_pnl_brier_delta=_optional_delta(
            catboost_evaluation.positive_realized_pnl_brier_score,
            baseline_evaluation.positive_realized_pnl_brier_score,
        ),
    )
