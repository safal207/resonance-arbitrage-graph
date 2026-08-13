from copy import deepcopy
import hashlib
import json

import pytest

from resonance_arbitrage_graph.joint_holdout import JointPolicyCandidate
from resonance_arbitrage_graph.policy_promotion import (
    CalibrationCandidateSupport,
    PolicyPromotionGuardrails,
    PolicyPromotionStatus,
    _decision_for_support,
    run_policy_promotion,
    verify_policy_promotion_bundle_binding,
    verify_policy_promotion_report_envelope,
)
from resonance_arbitrage_graph.stability_decomposition import DecompositionStatus, run_stability_decomposition
from resonance_arbitrage_graph.walk_forward import WalkForwardStatus, run_walk_forward_stability
from test_walk_forward import _bundle, _grid, _policy


def _canonical_sha(payload: dict) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _stable_chain():
    bundle = _bundle()
    walk = run_walk_forward_stability(bundle, _grid(), _policy())
    decomposition = run_stability_decomposition(bundle, walk)
    return bundle, walk, decomposition


def _support(candidate, folds, passed):
    failed = tuple(index for index in folds if index not in set(passed))
    return CalibrationCandidateSupport(candidate, folds, passed, failed)


def test_stable_consensus_is_promoted_and_reproducible():
    bundle, walk, decomposition = _stable_chain()
    report = run_policy_promotion(bundle, walk, decomposition)
    assert report.decision.status is PolicyPromotionStatus.PROMOTED
    assert report.decision.candidate == JointPolicyCandidate(35.0, 20.0)
    assert report.decision.consensus_fraction == 1.0
    assert report.decision.candidate_validation_pass_rate == 1.0
    assert verify_policy_promotion_report_envelope(report.to_envelope()) == report.canonical_payload()
    assert verify_policy_promotion_bundle_binding(report, walk, decomposition, bundle) is True


def test_unstable_walk_forward_blocks_promotion():
    bundle = _bundle(bad_validation_truth=True)
    walk = run_walk_forward_stability(bundle, _grid(), _policy(min_pass_rate=1.0))
    decomposition = run_stability_decomposition(bundle, walk)
    report = run_policy_promotion(bundle, walk, decomposition)
    assert report.decision.status is PolicyPromotionStatus.BLOCKED_WALK_FORWARD
    assert report.decision.candidate is None


def test_calibration_consensus_tie_fails_closed():
    support = (
        _support(JointPolicyCandidate(30.0, 20.0), (1,), (1,)),
        _support(JointPolicyCandidate(35.0, 40.0), (2,), (2,)),
    )
    guardrails = PolicyPromotionGuardrails(min_selected_policy_folds=2, min_candidate_supporting_folds=1, min_consensus_fraction=0.0, min_candidate_validation_pass_rate=0.0)
    decision = _decision_for_support(WalkForwardStatus.PASSED_STABILITY, DecompositionStatus.STABLE_BASELINE, support, guardrails)
    assert decision.status is PolicyPromotionStatus.AMBIGUOUS_CALIBRATION_CONSENSUS
    assert decision.candidate is None


def test_validation_veto_never_selects_fallback():
    winner = JointPolicyCandidate(30.0, 20.0)
    fallback = JointPolicyCandidate(35.0, 40.0)
    support = (_support(winner, (1, 2), (1,)), _support(fallback, (3,), (3,)))
    guardrails = PolicyPromotionGuardrails(min_selected_policy_folds=3, min_candidate_supporting_folds=2, min_consensus_fraction=0.5, min_candidate_validation_pass_rate=0.75)
    decision = _decision_for_support(WalkForwardStatus.PASSED_STABILITY, DecompositionStatus.STABLE_BASELINE, support, guardrails)
    assert decision.status is PolicyPromotionStatus.CANDIDATE_VALIDATION_BELOW_FLOOR
    assert decision.candidate == winner
    assert decision.candidate != fallback


def test_decision_tamper_is_rejected_even_with_recomputed_sha():
    bundle, walk, decomposition = _stable_chain()
    report = run_policy_promotion(bundle, walk, decomposition)
    envelope = deepcopy(report.to_envelope())
    envelope["payload"]["decision"]["status"] = PolicyPromotionStatus.CONSENSUS_BELOW_FLOOR.value
    envelope["sha256"] = _canonical_sha(envelope["payload"])
    with pytest.raises(ValueError, match="decision does not match"):
        verify_policy_promotion_report_envelope(envelope)


def test_promotion_receipt_is_deterministic():
    bundle, walk, decomposition = _stable_chain()
    first = run_policy_promotion(bundle, walk, decomposition)
    second = run_policy_promotion(bundle, walk, decomposition)
    assert first.sha256 == second.sha256
    assert first.canonical_payload() == second.canonical_payload()
