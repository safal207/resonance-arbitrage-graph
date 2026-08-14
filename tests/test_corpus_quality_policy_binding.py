from __future__ import annotations

import pytest

from resonance_arbitrage_graph.corpus_quality import (
    CorpusQualityPolicy,
    CorpusQualityReport,
)


def test_quality_policy_payload_round_trip_preserves_identity():
    policy = CorpusQualityPolicy(
        min_decision_batches=12,
        min_effective_decision_batches=7.5,
        min_temporal_span_ms=90_000,
        min_distinct_routes=4,
        min_effective_routes=2.5,
        min_distinct_route_markets=5,
        min_distinct_regimes=2,
    )

    rebuilt = CorpusQualityPolicy.from_payload(policy.to_payload())

    assert rebuilt == policy
    assert rebuilt.sha256 == policy.sha256


def test_quality_report_rejects_policy_digest_not_supported_by_payload():
    policy = CorpusQualityPolicy()

    with pytest.raises(ValueError, match="policy SHA-256 does not match payload"):
        CorpusQualityReport(
            corpus_sha256="a" * 64,
            policy_sha256="0" * 64,
            policy_payload=policy.to_payload(),
            terminal_operation_count=0,
            decision_batch_counts=(),
            effective_decision_batches=0.0,
            largest_decision_batch_share=0.0,
            temporal_span_ms=0,
            route_topology_counts=(),
            effective_routes=0.0,
            largest_route_share=0.0,
            route_market_identities=(),
            regime_counts=(),
            failed_dimensions=("decision_batches",),
            quality_ready=False,
        )


def test_quality_policy_rejects_noncanonical_extra_fields():
    policy = CorpusQualityPolicy()
    payload = policy.to_payload()
    payload["hidden_override"] = True

    with pytest.raises(ValueError, match="not canonical"):
        CorpusQualityPolicy.from_payload(payload)
