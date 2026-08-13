from copy import deepcopy
import hashlib
import json

import pytest

from resonance_arbitrage_graph.holdout import HoldoutPolicy
from resonance_arbitrage_graph.joint_holdout import (
    JointCandidateGrid,
    JointHoldoutPolicy,
    JointHoldoutReport,
    JointHoldoutStatus,
    JointPolicyContext,
    verify_joint_holdout_report_envelope,
)


def _sha256(payload) -> str:
    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _raw_context():
    return {
        "engine_policy": {
            "observe_net_edge": 0.0,
            "max_quote_age_ms": 3000,
        },
        "regime_policy": {
            "thin_capacity_ratio": 1.25,
            "wide_spread_bps": 25.0,
        },
        "regime_execution_policy": {
            "schema": "resonance.arbitrage.regime-execution-policy/v0.1",
            "normal": "ALLOW",
            "volatile": "OBSERVE_ONLY",
            "thin_liquidity": "OBSERVE_ONLY",
            "dislocated": "OBSERVE_ONLY",
            "unknown": "REJECT",
        },
        "rolling_window_policy": {
            "horizon_ms": 60000,
            "min_samples": 5,
            "min_coverage_ratio": 0.8,
        },
    }


def _context() -> JointPolicyContext:
    raw = _raw_context()
    return JointPolicyContext(
        sha256=_sha256(raw),
        baseline_execute_net_edge_bps=30.0,
        baseline_volatile_return_bps=75.0,
        observe_net_edge_bps=0.0,
        frozen_context=raw,
    )


def _joint_policy() -> JointHoldoutPolicy:
    return JointHoldoutPolicy(
        holdout=HoldoutPolicy(
            validation_fraction=0.5,
            min_calibration_operations=1,
            min_validation_operations=1,
            min_calibration_truth_events=1,
            min_validation_truth_events=1,
            min_truth_rate_lower_bound=0.0,
            min_survival_rate_lower_bound=0.0,
            confidence_z=0.0,
        )
    )


def test_joint_policy_context_copies_and_recursively_freezes_raw_context():
    raw = _raw_context()
    context = JointPolicyContext(
        sha256=_sha256(raw),
        baseline_execute_net_edge_bps=30.0,
        baseline_volatile_return_bps=75.0,
        observe_net_edge_bps=0.0,
        frozen_context=raw,
    )
    payload_before = context.to_payload()

    raw["engine_policy"]["max_quote_age_ms"] = 1

    assert context.to_payload() == payload_before
    with pytest.raises(TypeError):
        context.frozen_context["engine_policy"]["max_quote_age_ms"] = 1


def test_joint_policy_context_rejects_mismatched_inner_digest():
    with pytest.raises(ValueError, match="context SHA-256"):
        JointPolicyContext(
            sha256="0" * 64,
            baseline_execute_net_edge_bps=30.0,
            baseline_volatile_return_bps=75.0,
            observe_net_edge_bps=0.0,
            frozen_context=_raw_context(),
        )


def test_joint_report_rejects_forged_inner_context_even_with_recomputed_outer_digest():
    report = JointHoldoutReport(
        source_bundle_sha256="a" * 64,
        policy_context=_context(),
        joint_policy=_joint_policy(),
        candidate_grid=JointCandidateGrid(
            execute_net_edge_bps=(35.0,),
            volatile_return_bps=(20.0,),
        ),
        status=JointHoldoutStatus.INSUFFICIENT_CORPUS,
        split=None,
        calibration_evaluations=(),
        selected_candidate=None,
        validation_evaluation=None,
        reasons=("fixture",),
    )
    envelope = deepcopy(report.to_envelope())
    envelope["payload"]["policy_context"]["frozen_context"]["engine_policy"][
        "max_quote_age_ms"
    ] = 1
    envelope["sha256"] = _sha256(envelope["payload"])

    with pytest.raises(ValueError, match="policy context SHA-256"):
        verify_joint_holdout_report_envelope(envelope)
