from __future__ import annotations

from dataclasses import asdict
import hashlib
import json
from collections.abc import Sequence

from .engine import PaperExecution
from .evidence import EvidenceReceipt
from .market_evidence import make_market_evidence_receipt
from .model import Edge, RouteResult
from .quotes import QuoteSnapshot
from .regime import RegimeClassification, RegimePolicy, classify_market_regime
from .regime_features import derive_route_regime_features


def make_regime_market_evidence_receipt(
    operation_id: str,
    edges: Sequence[Edge],
    result: RouteResult,
    *,
    snapshots: Sequence[QuoteSnapshot],
    evaluation_time_ms: int,
    classification: RegimeClassification,
    regime_policy: RegimePolicy | None = None,
    execution: PaperExecution | None = None,
) -> EvidenceReceipt:
    """Create market evidence that also proves the derived regime inputs/policy."""

    regime_policy = regime_policy or RegimePolicy()
    recomputed_features = derive_route_regime_features(
        edges,
        snapshots,
        evaluation_time_ms=evaluation_time_ms,
        start_amount=result.start_amount,
        short_window_return_volatility_bps=(
            classification.features.short_window_return_volatility_bps
        ),
    )
    if recomputed_features != classification.features:
        raise ValueError("regime features do not match route-bound market snapshots")

    recomputed_classification = classify_market_regime(
        recomputed_features,
        policy=regime_policy,
    )
    if recomputed_classification != classification:
        raise ValueError("regime classification does not match supplied policy/features")

    receipt = make_market_evidence_receipt(
        operation_id,
        edges,
        result,
        snapshots=snapshots,
        evaluation_time_ms=evaluation_time_ms,
        execution=execution,
    )
    payload = dict(receipt.payload)
    payload["market_regime"] = {
        "regime": classification.regime.value,
        "features": classification.features.to_context(),
        "feature_provenance": {
            "normalized_spread_bps": "route_bound_public_quotes",
            "top_of_book_capacity_ratio": "route_bound_edge_capacity",
            "quote_age_ms": "route_bound_public_quotes",
            "quote_age_dispersion_ms": "route_bound_public_quotes",
            "cross_rate_dislocation_bps": "route_bound_raw_edge_rates",
            "short_window_return_volatility_bps": (
                "caller_supplied_explicit_feature"
                if classification.features.short_window_return_volatility_bps is not None
                else "not_supplied"
            ),
        },
        "reasons": list(classification.reasons),
        "policy": asdict(regime_policy),
    }

    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return EvidenceReceipt(payload=payload, sha256=digest)
