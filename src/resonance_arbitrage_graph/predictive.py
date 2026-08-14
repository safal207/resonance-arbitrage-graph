from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass
from enum import Enum
import hashlib
import hmac
import json
import math
from statistics import mean
from types import MappingProxyType
from typing import Any

from .model import Verdict
from .replay import ReplayBundle, ReplayCase, replay_case
from .window_regime import derive_window_regime_context


_FEATURE_SCHEMA = "resonance.arbitrage.opportunity-feature-vector/v0.1"
_DATASET_SCHEMA = "resonance.arbitrage.predictive-dataset/v0.1"
_TRAINING_MANIFEST_SCHEMA = "resonance.arbitrage.predictive-training-manifest/v0.1"
_MODEL_ARTIFACT_SCHEMA = "resonance.arbitrage.predictive-model-artifact/v0.1"
_PREDICTION_RECEIPT_SCHEMA = "resonance.arbitrage.predictive-opportunity-receipt/v0.1"
_MODEL_PREFIX = "pmo_"


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
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ValueError(f"{name} must be numeric")
    value = float(value)
    if not math.isfinite(value) or not 0.0 <= value <= 1.0:
        raise ValueError(f"{name} must be finite and between 0 and 1")
    return value


def _sha256_text(value: str, name: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise ValueError(f"{name} must be a lowercase SHA-256 digest")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{name} must be hexadecimal") from exc
    if value.lower() != value:
        raise ValueError(f"{name} must be lowercase")
    return value


class PredictionTarget(str, Enum):
    FUTURE_NET_EDGE_BPS = "FUTURE_NET_EDGE_BPS"
    SURVIVAL_PROBABILITY = "SURVIVAL_PROBABILITY"
    POSITIVE_REALIZED_PNL_PROBABILITY = "POSITIVE_REALIZED_PNL_PROBABILITY"


@dataclass(frozen=True, slots=True)
class OpportunityFeatureVector:
    logical_operation_id: str
    decision_at_ms: int
    route_id: str
    start_amount: float
    deterministic_verdict: str
    market_regime: str
    expected_edge_bps: float
    required_edge_bps: float
    route_hops: int
    total_cost_bps: float
    total_latency_ms: int
    route_success_probability: float
    normalized_spread_bps: float
    top_of_book_capacity_ratio: float
    quote_age_ms: int
    quote_age_dispersion_ms: int
    cross_rate_dislocation_bps: float | None
    short_window_return_volatility_bps: float | None
    min_window_sample_count: int
    min_window_coverage_ratio: float
    venue_sequence: tuple[str, ...]
    symbol_sequence: tuple[str, ...]
    side_sequence: tuple[str, ...]
    asset_path: tuple[str, ...]
    same_venue: bool
    policy_context_sha256: str
    source_replay_case_sha256: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "venue_sequence", tuple(self.venue_sequence))
        object.__setattr__(self, "symbol_sequence", tuple(self.symbol_sequence))
        object.__setattr__(self, "side_sequence", tuple(self.side_sequence))
        object.__setattr__(self, "asset_path", tuple(self.asset_path))

        for name in ("logical_operation_id", "route_id", "deterministic_verdict", "market_regime"):
            if not isinstance(getattr(self, name), str) or not getattr(self, name):
                raise ValueError(f"{name} must be non-empty")
        if self.deterministic_verdict not in {verdict.value for verdict in Verdict}:
            raise ValueError("deterministic_verdict is invalid")
        if self.decision_at_ms < 0:
            raise ValueError("decision_at_ms must be non-negative")
        if not math.isfinite(self.start_amount) or self.start_amount <= 0:
            raise ValueError("start_amount must be finite and positive")
        if not math.isfinite(self.expected_edge_bps):
            raise ValueError("expected_edge_bps must be finite")
        for name in (
            "required_edge_bps",
            "total_cost_bps",
            "normalized_spread_bps",
            "top_of_book_capacity_ratio",
        ):
            value = getattr(self, name)
            if not math.isfinite(value) or value < 0:
                raise ValueError(f"{name} must be finite and non-negative")
        if self.top_of_book_capacity_ratio <= 0:
            raise ValueError("top_of_book_capacity_ratio must be positive")
        if self.route_hops < 1 or self.min_window_sample_count < 1:
            raise ValueError("route_hops and min_window_sample_count must be positive")
        if self.total_latency_ms < 0 or self.quote_age_ms < 0 or self.quote_age_dispersion_ms < 0:
            raise ValueError("latency and quote ages must be non-negative")
        _probability(self.route_success_probability, "route_success_probability")
        _probability(self.min_window_coverage_ratio, "min_window_coverage_ratio")
        for name in ("cross_rate_dislocation_bps", "short_window_return_volatility_bps"):
            value = getattr(self, name)
            if value is not None and (not math.isfinite(value) or value < 0):
                raise ValueError(f"{name} must be finite and non-negative when supplied")
        if len(self.venue_sequence) != self.route_hops:
            raise ValueError("venue_sequence length must equal route_hops")
        if len(self.symbol_sequence) != self.route_hops:
            raise ValueError("symbol_sequence length must equal route_hops")
        if len(self.side_sequence) != self.route_hops:
            raise ValueError("side_sequence length must equal route_hops")
        if len(self.asset_path) != self.route_hops + 1:
            raise ValueError("asset_path must contain one more item than route_hops")
        for sequence_name in ("venue_sequence", "symbol_sequence", "side_sequence", "asset_path"):
            sequence = getattr(self, sequence_name)
            if any(not isinstance(value, str) or not value for value in sequence):
                raise ValueError(f"{sequence_name} values must be non-empty strings")
        if not isinstance(self.same_venue, bool):
            raise ValueError("same_venue must be bool")
        _sha256_text(self.policy_context_sha256, "policy_context_sha256")
        _sha256_text(self.source_replay_case_sha256, "source_replay_case_sha256")

    def canonical_payload(self) -> dict[str, Any]:
        return {
            "schema": _FEATURE_SCHEMA,
            "logical_operation_id": self.logical_operation_id,
            "decision_at_ms": self.decision_at_ms,
            "route_id": self.route_id,
            "start_amount": self.start_amount,
            "deterministic_verdict": self.deterministic_verdict,
            "market_regime": self.market_regime,
            "expected_edge_bps": self.expected_edge_bps,
            "required_edge_bps": self.required_edge_bps,
            "route_hops": self.route_hops,
            "total_cost_bps": self.total_cost_bps,
            "total_latency_ms": self.total_latency_ms,
            "route_success_probability": self.route_success_probability,
            "normalized_spread_bps": self.normalized_spread_bps,
            "top_of_book_capacity_ratio": self.top_of_book_capacity_ratio,
            "quote_age_ms": self.quote_age_ms,
            "quote_age_dispersion_ms": self.quote_age_dispersion_ms,
            "cross_rate_dislocation_bps": self.cross_rate_dislocation_bps,
            "short_window_return_volatility_bps": self.short_window_return_volatility_bps,
            "min_window_sample_count": self.min_window_sample_count,
            "min_window_coverage_ratio": self.min_window_coverage_ratio,
            "venue_sequence": list(self.venue_sequence),
            "symbol_sequence": list(self.symbol_sequence),
            "side_sequence": list(self.side_sequence),
            "asset_path": list(self.asset_path),
            "same_venue": self.same_venue,
            "policy_context_sha256": self.policy_context_sha256,
            "source_replay_case_sha256": self.source_replay_case_sha256,
        }

    @property
    def sha256(self) -> str:
        return _sha256(self.canonical_payload())


@dataclass(frozen=True, slots=True)
class PredictiveTargetLabels:
    target_available_at_ms: int | None
    future_net_edge_bps: float | None
    survived: bool | None
    positive_realized_pnl: bool | None
    met_required_edge: bool | None
    realized_paper_pnl_units: float | None

    def __post_init__(self) -> None:
        if self.target_available_at_ms is not None and self.target_available_at_ms < 0:
            raise ValueError("target_available_at_ms must be non-negative")
        for name in ("future_net_edge_bps", "realized_paper_pnl_units"):
            value = getattr(self, name)
            if value is not None and not math.isfinite(value):
                raise ValueError(f"{name} must be finite when supplied")
        flags = (self.survived, self.positive_realized_pnl, self.met_required_edge)
        if any(flag is not None and not isinstance(flag, bool) for flag in flags):
            raise ValueError("target flags must be bool or None")

        if self.target_available_at_ms is None:
            if (
                self.future_net_edge_bps is not None
                or self.realized_paper_pnl_units is not None
                or any(flag is not None for flag in flags)
            ):
                raise ValueError("unavailable target cannot carry labels")
            return

        if self.survived is None or self.positive_realized_pnl is None or self.met_required_edge is None:
            raise ValueError("available target must carry all classification labels")
        if self.survived:
            if self.future_net_edge_bps is None or self.realized_paper_pnl_units is None:
                raise ValueError("survived target requires realized edge and paper PnL")
            if self.positive_realized_pnl != (self.realized_paper_pnl_units > 0.0):
                raise ValueError("positive_realized_pnl conflicts with realized_paper_pnl_units")
        else:
            if self.future_net_edge_bps is not None or self.realized_paper_pnl_units is not None:
                raise ValueError("expired target cannot invent realized edge or paper PnL")
            if self.positive_realized_pnl or self.met_required_edge:
                raise ValueError("expired target cannot be positive or meet required edge")

    @property
    def available(self) -> bool:
        return self.target_available_at_ms is not None

    def to_payload(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class PredictiveRow:
    feature_vector: OpportunityFeatureVector
    targets: PredictiveTargetLabels

    def __post_init__(self) -> None:
        if (
            self.targets.target_available_at_ms is not None
            and self.targets.target_available_at_ms < self.feature_vector.decision_at_ms
        ):
            raise ValueError("target cannot be available before the decision")

    @property
    def logical_operation_id(self) -> str:
        return self.feature_vector.logical_operation_id

    @property
    def decision_at_ms(self) -> int:
        return self.feature_vector.decision_at_ms

    @property
    def start_amount(self) -> float:
        return self.feature_vector.start_amount

    def to_payload(self) -> dict[str, Any]:
        return {
            "feature_vector": self.feature_vector.canonical_payload(),
            "feature_vector_sha256": self.feature_vector.sha256,
            "targets": self.targets.to_payload(),
        }


def _policy_context_sha256(case: ReplayCase) -> str:
    return _sha256(
        {
            "engine_policy": asdict(case.engine_policy),
            "regime_policy": asdict(case.regime_policy),
            "regime_execution_policy": case.regime_execution_policy.canonical_payload(),
        }
    )


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
    summaries = tuple(context.window_summary_by_market[key] for key in sorted(context.window_summary_by_market))
    if not summaries:
        raise ValueError("predictive feature vector requires rolling-window summaries")

    snapshots_for_legs = [case.snapshots[leg.snapshot_index] for leg in case.legs]
    venue_sequence = tuple(snapshot.venue for snapshot in snapshots_for_legs)
    symbol_sequence = tuple(snapshot.symbol for snapshot in snapshots_for_legs)
    side_sequence = tuple(leg.side.value for leg in case.legs)
    asset_path = tuple([route[0].src.asset, *[edge.dst.asset for edge in route]])

    feature_vector = OpportunityFeatureVector(
        logical_operation_id=case.logical_operation_id,
        decision_at_ms=case.evaluation_time_ms,
        route_id=case.route_id,
        start_amount=case.start_amount,
        deterministic_verdict=result.expected_verdict.value,
        market_regime=result.regime.value,
        expected_edge_bps=result.expected_edge_bps,
        required_edge_bps=result.required_edge_bps,
        route_hops=len(route),
        total_cost_bps=sum(edge.total_cost_bps for edge in route),
        total_latency_ms=sum(edge.latency_ms for edge in route),
        route_success_probability=math.prod(edge.success_probability for edge in route),
        normalized_spread_bps=regime_features.normalized_spread_bps,
        top_of_book_capacity_ratio=regime_features.top_of_book_capacity_ratio,
        quote_age_ms=regime_features.quote_age_ms,
        quote_age_dispersion_ms=regime_features.quote_age_dispersion_ms,
        cross_rate_dislocation_bps=regime_features.cross_rate_dislocation_bps,
        short_window_return_volatility_bps=regime_features.short_window_return_volatility_bps,
        min_window_sample_count=min(summary.sample_count for summary in summaries),
        min_window_coverage_ratio=min(summary.coverage_ratio for summary in summaries),
        venue_sequence=venue_sequence,
        symbol_sequence=symbol_sequence,
        side_sequence=side_sequence,
        asset_path=asset_path,
        same_venue=len(set(venue_sequence)) == 1,
        policy_context_sha256=_policy_context_sha256(case),
        source_replay_case_sha256=case.sha256,
    )

    outcome = case.outcome
    if outcome.realized_net_edge_bps is not None:
        realized_pnl = case.start_amount * outcome.realized_net_edge_bps / 10_000.0
        targets = PredictiveTargetLabels(
            target_available_at_ms=outcome.observed_at_ms,
            future_net_edge_bps=outcome.realized_net_edge_bps,
            survived=True,
            positive_realized_pnl=realized_pnl > 0.0,
            met_required_edge=outcome.realized_net_edge_bps >= result.required_edge_bps,
            realized_paper_pnl_units=realized_pnl,
        )
    elif outcome.expired:
        targets = PredictiveTargetLabels(
            target_available_at_ms=outcome.observed_at_ms,
            future_net_edge_bps=None,
            survived=False,
            positive_realized_pnl=False,
            met_required_edge=False,
            realized_paper_pnl_units=None,
        )
    else:
        targets = PredictiveTargetLabels(
            target_available_at_ms=None,
            future_net_edge_bps=None,
            survived=None,
            positive_realized_pnl=None,
            met_required_edge=None,
            realized_paper_pnl_units=None,
        )

    return PredictiveRow(feature_vector=feature_vector, targets=targets)


@dataclass(frozen=True, slots=True)
class PredictiveDataset:
    source_bundle_sha256: str
    rows: tuple[PredictiveRow, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "rows", tuple(self.rows))
        _sha256_text(self.source_bundle_sha256, "source_bundle_sha256")
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
        object.__setattr__(self, "training_rows", tuple(self.training_rows))
        object.__setattr__(self, "validation_rows", tuple(self.validation_rows))
        object.__setattr__(self, "excluded_late_target_rows", tuple(self.excluded_late_target_rows))
        if not self.training_rows:
            raise ValueError("predictive split requires at least one training row")
        if not self.validation_rows:
            raise ValueError("predictive split requires at least one validation row")
        if self.validation_start_ms != self.validation_rows[0].decision_at_ms:
            raise ValueError("validation_start_ms must match the first validation decision")
        for row in self.training_rows:
            available_at = row.targets.target_available_at_ms
            if available_at is None or available_at > self.validation_start_ms:
                raise ValueError("training row target was unavailable at validation start")
            if row.decision_at_ms >= self.validation_start_ms:
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
    if not isinstance(validation_fraction, (int, float)) or isinstance(validation_fraction, bool):
        raise ValueError("validation_fraction must be numeric")
    validation_fraction = float(validation_fraction)
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
class PredictiveTrainingManifest:
    feature_schema_version: str
    training_rows_sha256: str
    training_operation_ids: tuple[str, ...]
    training_decision_start_ms: int
    training_decision_end_ms: int
    target_available_through_ms: int
    label_definition: str
    model_family: str
    model_config: Mapping[str, Any]

    def __post_init__(self) -> None:
        object.__setattr__(self, "training_operation_ids", tuple(self.training_operation_ids))
        object.__setattr__(self, "model_config", MappingProxyType(dict(self.model_config)))
        if self.feature_schema_version != _FEATURE_SCHEMA:
            raise ValueError("unsupported feature schema version")
        _sha256_text(self.training_rows_sha256, "training_rows_sha256")
        if not self.training_operation_ids or len(set(self.training_operation_ids)) != len(self.training_operation_ids):
            raise ValueError("training_operation_ids must be non-empty and unique")
        for name in ("label_definition", "model_family"):
            if not isinstance(getattr(self, name), str) or not getattr(self, name):
                raise ValueError(f"{name} must be non-empty")
        if self.training_decision_start_ms < 0 or self.training_decision_end_ms < self.training_decision_start_ms:
            raise ValueError("training decision bounds are invalid")
        if self.target_available_through_ms < self.training_decision_start_ms:
            raise ValueError("target availability bound is invalid")
        _canonical_json(dict(self.model_config))

    def canonical_payload(self) -> dict[str, Any]:
        return {
            "schema": _TRAINING_MANIFEST_SCHEMA,
            "feature_schema_version": self.feature_schema_version,
            "training_rows_sha256": self.training_rows_sha256,
            "training_operation_ids": list(self.training_operation_ids),
            "training_decision_start_ms": self.training_decision_start_ms,
            "training_decision_end_ms": self.training_decision_end_ms,
            "target_available_through_ms": self.target_available_through_ms,
            "label_definition": self.label_definition,
            "model_family": self.model_family,
            "model_config": dict(self.model_config),
        }

    @property
    def sha256(self) -> str:
        return _sha256(self.canonical_payload())


def build_training_manifest(
    rows: Sequence[PredictiveRow],
    *,
    model_family: str,
    model_config: Mapping[str, Any] | None = None,
) -> PredictiveTrainingManifest:
    rows = tuple(rows)
    if not rows:
        raise ValueError("training manifest requires rows")
    if any(not row.targets.available for row in rows):
        raise ValueError("training manifest only accepts rows with available targets")
    rows_payload = [row.to_payload() for row in rows]
    return PredictiveTrainingManifest(
        feature_schema_version=_FEATURE_SCHEMA,
        training_rows_sha256=_sha256(rows_payload),
        training_operation_ids=tuple(row.logical_operation_id for row in rows),
        training_decision_start_ms=min(row.decision_at_ms for row in rows),
        training_decision_end_ms=max(row.decision_at_ms for row in rows),
        target_available_through_ms=max(row.targets.target_available_at_ms or 0 for row in rows),
        label_definition=(
            "future_net_edge_bps from later replay outcome; survived=false for explicit expiry; "
            "positive_realized_pnl iff realized paper pnl > 0"
        ),
        model_family=model_family,
        model_config=dict(model_config or {}),
    )


@dataclass(frozen=True, slots=True)
class PredictiveModelArtifact:
    model_family: str
    training_manifest_sha256: str
    parameters: Mapping[str, Any]

    def __post_init__(self) -> None:
        object.__setattr__(self, "parameters", MappingProxyType(dict(self.parameters)))
        if not isinstance(self.model_family, str) or not self.model_family:
            raise ValueError("model_family must be non-empty")
        _sha256_text(self.training_manifest_sha256, "training_manifest_sha256")
        _canonical_json(dict(self.parameters))

    def canonical_payload(self) -> dict[str, Any]:
        return {
            "schema": _MODEL_ARTIFACT_SCHEMA,
            "model_family": self.model_family,
            "training_manifest_sha256": self.training_manifest_sha256,
            "parameters": dict(self.parameters),
        }

    @property
    def sha256(self) -> str:
        return _sha256(self.canonical_payload())

    @property
    def model_id(self) -> str:
        return _MODEL_PREFIX + self.sha256


@dataclass(frozen=True, slots=True)
class HistoricalMeanBaseline:
    manifest: PredictiveTrainingManifest
    artifact: PredictiveModelArtifact
    mean_future_net_edge_bps: float
    survival_probability: float
    positive_realized_pnl_probability: float

    @classmethod
    def fit(cls, rows: Sequence[PredictiveRow]) -> "HistoricalMeanBaseline":
        rows = tuple(rows)
        manifest = build_training_manifest(
            rows,
            model_family="historical_mean",
            model_config={"version": "v0.1"},
        )
        realized_edges = [
            row.targets.future_net_edge_bps
            for row in rows
            if row.targets.future_net_edge_bps is not None
        ]
        if not realized_edges:
            raise ValueError("historical baseline requires at least one realized edge target")
        survival_labels = [1.0 if row.targets.survived else 0.0 for row in rows]
        positive_labels = [1.0 if row.targets.positive_realized_pnl else 0.0 for row in rows]
        mean_edge = mean(realized_edges)
        survival_probability = mean(survival_labels)
        positive_probability = mean(positive_labels)
        artifact = PredictiveModelArtifact(
            model_family="historical_mean",
            training_manifest_sha256=manifest.sha256,
            parameters={
                "mean_future_net_edge_bps": mean_edge,
                "survival_probability": survival_probability,
                "positive_realized_pnl_probability": positive_probability,
            },
        )
        return cls(
            manifest=manifest,
            artifact=artifact,
            mean_future_net_edge_bps=mean_edge,
            survival_probability=survival_probability,
            positive_realized_pnl_probability=positive_probability,
        )

    @property
    def model_id(self) -> str:
        return self.artifact.model_id

    @property
    def trained_through_ms(self) -> int:
        return self.manifest.target_available_through_ms


@dataclass(frozen=True, slots=True)
class PredictiveOpportunityReceipt:
    logical_operation_id: str
    decision_timestamp_ms: int
    feature_schema_version: str
    feature_vector_sha256: str
    model_id: str
    model_artifact_sha256: str
    training_manifest_sha256: str
    prediction_target: PredictionTarget
    prediction_value: float
    prediction_timestamp_ms: int
    policy_context_sha256: str
    source_replay_case_sha256: str
    paper_only: bool = True

    def __post_init__(self) -> None:
        if not self.logical_operation_id:
            raise ValueError("logical_operation_id must be non-empty")
        if self.decision_timestamp_ms < 0 or self.prediction_timestamp_ms < 0:
            raise ValueError("prediction timestamps must be non-negative")
        if self.prediction_timestamp_ms != self.decision_timestamp_ms:
            raise ValueError("v0.16 prediction timestamp must equal decision timestamp")
        if self.feature_schema_version != _FEATURE_SCHEMA:
            raise ValueError("unsupported feature schema version")
        _sha256_text(self.feature_vector_sha256, "feature_vector_sha256")
        _sha256_text(self.model_artifact_sha256, "model_artifact_sha256")
        _sha256_text(self.training_manifest_sha256, "training_manifest_sha256")
        _sha256_text(self.policy_context_sha256, "policy_context_sha256")
        _sha256_text(self.source_replay_case_sha256, "source_replay_case_sha256")
        if self.model_id != _MODEL_PREFIX + self.model_artifact_sha256:
            raise ValueError("model_id must be content-derived from model artifact SHA-256")
        if not isinstance(self.prediction_target, PredictionTarget):
            raise ValueError("prediction_target must be PredictionTarget")
        if not math.isfinite(self.prediction_value):
            raise ValueError("prediction_value must be finite")
        if self.prediction_target in {
            PredictionTarget.SURVIVAL_PROBABILITY,
            PredictionTarget.POSITIVE_REALIZED_PNL_PROBABILITY,
        }:
            _probability(self.prediction_value, "prediction_value")
        if self.paper_only is not True:
            raise ValueError("predictive opportunity receipts are paper-only")

    def canonical_payload(self) -> dict[str, Any]:
        return {
            "schema": _PREDICTION_RECEIPT_SCHEMA,
            "logical_operation_id": self.logical_operation_id,
            "decision_timestamp_ms": self.decision_timestamp_ms,
            "feature_schema_version": self.feature_schema_version,
            "feature_vector_sha256": self.feature_vector_sha256,
            "model_id": self.model_id,
            "model_artifact_sha256": self.model_artifact_sha256,
            "training_manifest_sha256": self.training_manifest_sha256,
            "prediction_target": self.prediction_target.value,
            "prediction_value": self.prediction_value,
            "prediction_timestamp_ms": self.prediction_timestamp_ms,
            "policy_context_sha256": self.policy_context_sha256,
            "source_replay_case_sha256": self.source_replay_case_sha256,
            "paper_only": self.paper_only,
        }

    @property
    def sha256(self) -> str:
        return _sha256(self.canonical_payload())

    def to_envelope(self) -> dict[str, Any]:
        return {"payload": self.canonical_payload(), "sha256": self.sha256}


@dataclass(frozen=True, slots=True)
class PredictivePrediction:
    logical_operation_id: str
    model_id: str
    predicted_future_net_edge_bps: float
    survival_probability: float
    positive_realized_pnl_probability: float
    receipts: tuple[PredictiveOpportunityReceipt, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "receipts", tuple(self.receipts))
        if not self.logical_operation_id or not self.model_id:
            raise ValueError("prediction identifiers must be non-empty")
        if not math.isfinite(self.predicted_future_net_edge_bps):
            raise ValueError("predicted_future_net_edge_bps must be finite")
        _probability(self.survival_probability, "survival_probability")
        _probability(self.positive_realized_pnl_probability, "positive_realized_pnl_probability")
        if len(self.receipts) != 3:
            raise ValueError("prediction must bind exactly three target receipts")
        expected_targets = {
            PredictionTarget.FUTURE_NET_EDGE_BPS,
            PredictionTarget.SURVIVAL_PROBABILITY,
            PredictionTarget.POSITIVE_REALIZED_PNL_PROBABILITY,
        }
        if {receipt.prediction_target for receipt in self.receipts} != expected_targets:
            raise ValueError("prediction receipts do not cover all targets")
        if any(receipt.logical_operation_id != self.logical_operation_id for receipt in self.receipts):
            raise ValueError("prediction receipt logical operation mismatch")
        if any(receipt.model_id != self.model_id for receipt in self.receipts):
            raise ValueError("prediction receipt model mismatch")


def _make_prediction_receipt(
    row: PredictiveRow,
    model: HistoricalMeanBaseline,
    *,
    target: PredictionTarget,
    value: float,
) -> PredictiveOpportunityReceipt:
    if model.trained_through_ms > row.decision_at_ms:
        raise ValueError("model training used targets unavailable at prediction time")
    vector = row.feature_vector
    return PredictiveOpportunityReceipt(
        logical_operation_id=row.logical_operation_id,
        decision_timestamp_ms=row.decision_at_ms,
        feature_schema_version=_FEATURE_SCHEMA,
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


def predict_with_historical_baseline(
    model: HistoricalMeanBaseline,
    rows: Sequence[PredictiveRow],
) -> tuple[PredictivePrediction, ...]:
    predictions: list[PredictivePrediction] = []
    for row in rows:
        values = {
            PredictionTarget.FUTURE_NET_EDGE_BPS: model.mean_future_net_edge_bps,
            PredictionTarget.SURVIVAL_PROBABILITY: model.survival_probability,
            PredictionTarget.POSITIVE_REALIZED_PNL_PROBABILITY: model.positive_realized_pnl_probability,
        }
        receipts = tuple(
            _make_prediction_receipt(row, model, target=target, value=value)
            for target, value in values.items()
        )
        predictions.append(
            PredictivePrediction(
                logical_operation_id=row.logical_operation_id,
                model_id=model.model_id,
                predicted_future_net_edge_bps=model.mean_future_net_edge_bps,
                survival_probability=model.survival_probability,
                positive_realized_pnl_probability=model.positive_realized_pnl_probability,
                receipts=receipts,
            )
        )
    return tuple(predictions)


def verify_predictive_receipt_binding(
    receipt: PredictiveOpportunityReceipt,
    row: PredictiveRow,
    model: HistoricalMeanBaseline,
) -> None:
    vector = row.feature_vector
    if receipt.logical_operation_id != row.logical_operation_id:
        raise ValueError("receipt logical operation does not match row")
    if receipt.decision_timestamp_ms != row.decision_at_ms:
        raise ValueError("receipt decision timestamp does not match row")
    if not hmac.compare_digest(receipt.feature_vector_sha256, vector.sha256):
        raise ValueError("receipt feature vector SHA-256 does not match row")
    if not hmac.compare_digest(receipt.policy_context_sha256, vector.policy_context_sha256):
        raise ValueError("receipt policy context does not match row")
    if not hmac.compare_digest(receipt.source_replay_case_sha256, vector.source_replay_case_sha256):
        raise ValueError("receipt source replay case does not match row")
    if receipt.model_id != model.model_id:
        raise ValueError("receipt model_id does not match model artifact")
    if not hmac.compare_digest(receipt.model_artifact_sha256, model.artifact.sha256):
        raise ValueError("receipt model artifact SHA-256 does not match model")
    if not hmac.compare_digest(receipt.training_manifest_sha256, model.manifest.sha256):
        raise ValueError("receipt training manifest SHA-256 does not match model")
    if model.trained_through_ms > row.decision_at_ms:
        raise ValueError("receipt model training horizon exceeds decision time")


@dataclass(frozen=True, slots=True)
class ShadowEvaluation:
    evaluated_rows: int
    realized_edge_rows: int
    mean_absolute_edge_error_bps: float | None
    survival_brier_score: float | None
    positive_realized_pnl_brier_score: float | None
    deterministic_execute_rows: int
    selected_rows: int
    blocked_promotion_rows: int
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
    min_positive_realized_pnl_probability: float = 0.50,
) -> ShadowEvaluation:
    min_survival_probability = _probability(
        min_survival_probability,
        "min_survival_probability",
    )
    min_positive_realized_pnl_probability = _probability(
        min_positive_realized_pnl_probability,
        "min_positive_realized_pnl_probability",
    )
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
    evaluated_rows = 0
    realized_edge_rows = 0
    deterministic_execute_rows = 0
    selected_rows = 0
    blocked_promotion_rows = 0
    selected_realized_rows = 0
    selected_expired_rows = 0
    selected_realized_pnl_units = 0.0

    for row in rows:
        if not row.targets.available:
            continue
        try:
            prediction = prediction_by_operation[row.logical_operation_id]
        except KeyError as exc:
            raise ValueError("missing prediction for an evaluable row") from exc
        if prediction.model_id == "":
            raise ValueError("prediction model_id must be non-empty")
        for receipt in prediction.receipts:
            if receipt.decision_timestamp_ms != row.decision_at_ms:
                raise ValueError("prediction receipt decision timestamp mismatch")
        evaluated_rows += 1

        if row.targets.future_net_edge_bps is not None:
            realized_edge_rows += 1
            edge_errors.append(
                abs(
                    prediction.predicted_future_net_edge_bps
                    - row.targets.future_net_edge_bps
                )
            )
        survival_label = 1.0 if row.targets.survived else 0.0
        positive_label = 1.0 if row.targets.positive_realized_pnl else 0.0
        survival_errors.append((prediction.survival_probability - survival_label) ** 2)
        positive_errors.append(
            (prediction.positive_realized_pnl_probability - positive_label) ** 2
        )

        model_positive = (
            prediction.predicted_future_net_edge_bps > 0.0
            and prediction.survival_probability >= min_survival_probability
            and prediction.positive_realized_pnl_probability
            >= min_positive_realized_pnl_probability
        )
        deterministic_execute = (
            row.feature_vector.deterministic_verdict == Verdict.EXECUTE_SIM.value
        )
        if deterministic_execute:
            deterministic_execute_rows += 1
        elif model_positive:
            blocked_promotion_rows += 1

        selected = deterministic_execute and model_positive
        if not selected:
            continue

        selected_rows += 1
        if row.targets.realized_paper_pnl_units is not None:
            selected_realized_rows += 1
            selected_realized_pnl_units += row.targets.realized_paper_pnl_units
        elif row.targets.survived is False:
            selected_expired_rows += 1

    if evaluated_rows == 0:
        raise ValueError("shadow evaluation requires available validation targets")

    return ShadowEvaluation(
        evaluated_rows=evaluated_rows,
        realized_edge_rows=realized_edge_rows,
        mean_absolute_edge_error_bps=mean(edge_errors) if edge_errors else None,
        survival_brier_score=mean(survival_errors) if survival_errors else None,
        positive_realized_pnl_brier_score=mean(positive_errors) if positive_errors else None,
        deterministic_execute_rows=deterministic_execute_rows,
        selected_rows=selected_rows,
        blocked_promotion_rows=blocked_promotion_rows,
        selected_realized_rows=selected_realized_rows,
        selected_expired_rows=selected_expired_rows,
        selected_realized_pnl_units=selected_realized_pnl_units,
    )
