from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
import hashlib
import hmac
import json
import math
import re
from typing import Any

from .evidence import EvidenceReceipt


_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_ALLOWED_VERDICTS = {"EXECUTE_SIM", "OBSERVE", "REJECT"}
_ALLOWED_MARKET_REGIMES = {
    "NORMAL",
    "VOLATILE",
    "THIN_LIQUIDITY",
    "DISLOCATED",
    "UNKNOWN",
}


class OutcomeClass(str, Enum):
    TRUE_POSITIVE = "TRUE_POSITIVE"
    FALSE_POSITIVE = "FALSE_POSITIVE"
    EXPIRED = "EXPIRED"
    REJECTED = "REJECTED"
    INDETERMINATE = "INDETERMINATE"

    @property
    def terminal(self) -> bool:
        return self is not OutcomeClass.INDETERMINATE


def verify_evidence_receipt(receipt: EvidenceReceipt) -> None:
    if not _SHA256_RE.fullmatch(receipt.sha256):
        raise ValueError("evidence receipt SHA-256 is malformed")
    digest = hashlib.sha256(receipt.canonical_json().encode("utf-8")).hexdigest()
    if not hmac.compare_digest(digest, receipt.sha256):
        raise ValueError("evidence receipt SHA-256 does not match payload")


def _merge_regime_context_from_receipt(
    payload: dict[str, Any],
    market_context: dict[str, Any] | None,
) -> dict[str, Any]:
    context = dict(market_context or {})
    regime_payload = payload.get("market_regime")
    if regime_payload is None:
        return context
    if not isinstance(regime_payload, dict):
        raise ValueError("evidence market_regime must be an object")

    regime = regime_payload.get("regime")
    features = regime_payload.get("features")
    reasons = regime_payload.get("reasons")
    if regime not in _ALLOWED_MARKET_REGIMES:
        raise ValueError("evidence market_regime has invalid regime")
    if not isinstance(features, dict):
        raise ValueError("evidence market_regime features must be an object")
    if not isinstance(reasons, list) or not reasons or any(
        not isinstance(reason, str) or not reason
        for reason in reasons
    ):
        raise ValueError("evidence market_regime reasons must be non-empty strings")

    derived = {
        "regime": regime,
        "regime_features": dict(features),
        "regime_reasons": list(reasons),
    }
    for key, value in derived.items():
        if key in context and context[key] != value:
            raise ValueError(f"market_context conflicts with evidence-bound regime field: {key}")
        context[key] = value

    try:
        json.dumps(context, sort_keys=True, ensure_ascii=False, allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise ValueError("evidence-bound market_context must be strict JSON") from exc
    return context


def classify_outcome(
    *,
    expected_verdict: str,
    observed_edge_bps: float | None,
    required_edge_bps: float,
    expired: bool = False,
) -> OutcomeClass:
    if expected_verdict not in _ALLOWED_VERDICTS:
        raise ValueError("unknown expected verdict")
    if not math.isfinite(required_edge_bps) or required_edge_bps < 0:
        raise ValueError("required_edge_bps must be finite and non-negative")
    if observed_edge_bps is not None and not math.isfinite(observed_edge_bps):
        raise ValueError("observed_edge_bps must be finite")

    if expected_verdict == "REJECT":
        return OutcomeClass.REJECTED
    if expected_verdict != "EXECUTE_SIM":
        return OutcomeClass.INDETERMINATE
    if expired:
        if observed_edge_bps is not None:
            raise ValueError("expired opportunity cannot have an observed paper outcome")
        return OutcomeClass.EXPIRED
    if observed_edge_bps is None:
        return OutcomeClass.INDETERMINATE
    if observed_edge_bps >= required_edge_bps:
        return OutcomeClass.TRUE_POSITIVE
    return OutcomeClass.FALSE_POSITIVE


@dataclass(frozen=True, slots=True)
class OpportunityObservation:
    logical_operation_id: str
    execution_id: str
    attempt: int
    opportunity_id: str
    route_id: str
    detected_at_ms: int
    observed_at_ms: int
    expected_verdict: str
    required_edge_bps: float
    expected_edge_bps: float
    observed_edge_bps: float | None
    outcome_class: OutcomeClass
    evidence_sha256: str
    market_context: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in (
            "logical_operation_id",
            "execution_id",
            "opportunity_id",
            "route_id",
        ):
            if not getattr(self, name):
                raise ValueError(f"{name} must be non-empty")
        if self.attempt < 1:
            raise ValueError("attempt must be >= 1")
        if self.detected_at_ms < 0 or self.observed_at_ms < 0:
            raise ValueError("timestamps cannot be negative")
        if self.observed_at_ms < self.detected_at_ms:
            raise ValueError("observed_at_ms cannot precede detected_at_ms")
        if self.expected_verdict not in _ALLOWED_VERDICTS:
            raise ValueError("unknown expected verdict")
        if not math.isfinite(self.required_edge_bps) or self.required_edge_bps < 0:
            raise ValueError("required_edge_bps must be finite and non-negative")
        if not math.isfinite(self.expected_edge_bps):
            raise ValueError("expected_edge_bps must be finite")
        if self.observed_edge_bps is not None and not math.isfinite(self.observed_edge_bps):
            raise ValueError("observed_edge_bps must be finite")
        if not _SHA256_RE.fullmatch(self.evidence_sha256):
            raise ValueError("evidence_sha256 must be lowercase SHA-256")

        derived = classify_outcome(
            expected_verdict=self.expected_verdict,
            observed_edge_bps=self.observed_edge_bps,
            required_edge_bps=self.required_edge_bps,
            expired=self.outcome_class is OutcomeClass.EXPIRED,
        )
        if derived is not self.outcome_class:
            raise ValueError("outcome_class is inconsistent with observation inputs")

        context = dict(self.market_context)
        try:
            json.dumps(context, sort_keys=True, allow_nan=False)
        except (TypeError, ValueError) as exc:
            raise ValueError("market_context must be strict JSON") from exc
        object.__setattr__(self, "market_context", context)

    @property
    def prediction_error_bps(self) -> float | None:
        if self.observed_edge_bps is None:
            return None
        return self.observed_edge_bps - self.expected_edge_bps

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["outcome_class"] = self.outcome_class.value
        data["prediction_error_bps"] = self.prediction_error_bps
        return data

    def canonical_json(self) -> str:
        return json.dumps(
            self.to_dict(),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "OpportunityObservation":
        payload = dict(data)
        stored_error = payload.pop("prediction_error_bps", None)
        payload["outcome_class"] = OutcomeClass(payload["outcome_class"])
        observation = cls(**payload)
        if stored_error != observation.prediction_error_bps:
            raise ValueError("stored prediction_error_bps is inconsistent")
        return observation


def observation_from_evidence(
    receipt: EvidenceReceipt,
    *,
    execution_id: str,
    attempt: int,
    opportunity_id: str,
    route_id: str,
    detected_at_ms: int,
    observed_at_ms: int,
    required_edge_bps: float = 0.0,
    expired: bool = False,
    market_context: dict[str, Any] | None = None,
) -> OpportunityObservation:
    verify_evidence_receipt(receipt)
    payload = receipt.payload
    if payload.get("paper_only") is not True:
        raise ValueError("observation memory only accepts paper-only evidence")

    logical_operation_id = payload.get("logical_operation_id")
    if not isinstance(logical_operation_id, str) or not logical_operation_id:
        raise ValueError("evidence receipt has no logical_operation_id")

    expected = payload.get("expected")
    if not isinstance(expected, dict):
        raise ValueError("evidence receipt has no expected result")
    expected_verdict = expected.get("verdict")
    expected_net_edge = expected.get("net_edge")
    if expected_verdict not in _ALLOWED_VERDICTS:
        raise ValueError("evidence receipt has invalid expected verdict")
    if not isinstance(expected_net_edge, (int, float)) or not math.isfinite(expected_net_edge):
        raise ValueError("evidence receipt has invalid expected net edge")

    observed_edge_bps: float | None = None
    observed = payload.get("observed")
    if observed is not None:
        if not isinstance(observed, dict):
            raise ValueError("evidence observed payload must be an object")
        realized = observed.get("realized_net_edge")
        if not isinstance(realized, (int, float)) or not math.isfinite(realized):
            raise ValueError("evidence receipt has invalid realized net edge")
        observed_edge_bps = float(realized) * 10_000.0

    expected_edge_bps = float(expected_net_edge) * 10_000.0
    outcome = classify_outcome(
        expected_verdict=expected_verdict,
        observed_edge_bps=observed_edge_bps,
        required_edge_bps=required_edge_bps,
        expired=expired,
    )
    bound_market_context = _merge_regime_context_from_receipt(payload, market_context)

    return OpportunityObservation(
        logical_operation_id=logical_operation_id,
        execution_id=execution_id,
        attempt=attempt,
        opportunity_id=opportunity_id,
        route_id=route_id,
        detected_at_ms=detected_at_ms,
        observed_at_ms=observed_at_ms,
        expected_verdict=expected_verdict,
        required_edge_bps=required_edge_bps,
        expected_edge_bps=expected_edge_bps,
        observed_edge_bps=observed_edge_bps,
        outcome_class=outcome,
        evidence_sha256=receipt.sha256,
        market_context=bound_market_context,
    )


def verify_observation_evidence_binding(
    observation: OpportunityObservation,
    receipt: EvidenceReceipt,
) -> None:
    rebuilt = observation_from_evidence(
        receipt,
        execution_id=observation.execution_id,
        attempt=observation.attempt,
        opportunity_id=observation.opportunity_id,
        route_id=observation.route_id,
        detected_at_ms=observation.detected_at_ms,
        observed_at_ms=observation.observed_at_ms,
        required_edge_bps=observation.required_edge_bps,
        expired=observation.outcome_class is OutcomeClass.EXPIRED,
        market_context=observation.market_context,
    )
    if rebuilt != observation:
        raise ValueError("observation fields do not match supplied evidence receipt")
