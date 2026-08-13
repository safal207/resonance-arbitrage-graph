from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence

from .evidence import EvidenceReceipt
from .model import Edge, RouteResult
from .quotes import QuoteSnapshot
from .regime import RegimePolicy
from .regime_evidence import make_regime_market_evidence_receipt
from .rolling_state import RollingMarketWindow
from .window_regime import derive_window_regime_context


def make_window_regime_evidence_receipt(
    operation_id: str,
    edges: Sequence[Edge],
    result: RouteResult,
    *,
    snapshots: Sequence[QuoteSnapshot],
    windows_by_market: Mapping[str, RollingMarketWindow],
    evaluation_time_ms: int,
    regime_policy: RegimePolicy | None = None,
) -> EvidenceReceipt:
    context = derive_window_regime_context(
        edges,
        snapshots,
        windows_by_market=windows_by_market,
        evaluation_time_ms=evaluation_time_ms,
        start_amount=result.start_amount,
        regime_policy=regime_policy,
    )
    receipt = make_regime_market_evidence_receipt(
        operation_id,
        edges,
        result,
        snapshots=snapshots,
        evaluation_time_ms=evaluation_time_ms,
        classification=context.classification,
        regime_policy=regime_policy,
    )

    payload = dict(receipt.payload)
    payload["rolling_market_state"] = {
        "schema": "resonance.arbitrage.rolling-state-evidence/v0.1",
        "markets": {
            key: {
                "sha256": context.window_sha256_by_market[key],
                "summary": context.window_summary_by_market[key].to_payload(),
                "window": windows_by_market[key].canonical_payload(),
            }
            for key in sorted(context.window_sha256_by_market)
        },
        "feature_binding": {
            "short_window_return_volatility_bps": "derived_from_rolling_window",
            "route_aggregation": "max_bound_market_volatility",
        },
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
