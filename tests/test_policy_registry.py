import pytest

from resonance_arbitrage_graph.joint_holdout import JointCandidateGrid
from resonance_arbitrage_graph.policy_promotion import PolicyPromotionStatus, run_policy_promotion
from resonance_arbitrage_graph.policy_registry import PolicyRegistry, PolicyReleaseStatus, verify_policy_registry_envelope
from resonance_arbitrage_graph.policy_registry_binding import PolicyReleaseBinding, verify_policy_registry_full_bindings
from resonance_arbitrage_graph.stability_decomposition import run_stability_decomposition
from resonance_arbitrage_graph.walk_forward import run_walk_forward_stability
from test_walk_forward import _bundle, _grid, _policy


def _binding(grid=None):
    bundle = _bundle()
    walk = run_walk_forward_stability(bundle, grid or _grid(), _policy())
    decomposition = run_stability_decomposition(bundle, walk)
    promotion = run_policy_promotion(bundle, walk, decomposition)
    assert promotion.decision.status is PolicyPromotionStatus.PROMOTED
    return PolicyReleaseBinding(promotion, walk, decomposition, bundle)


def _alternate():
    return _binding(JointCandidateGrid(execute_net_edge_bps=(36.0,), volatile_return_bps=(20.0,)))


def test_release_supersede_and_full_binding():
    first, second = _binding(), _alternate()
    registry = PolicyRegistry.create(first.promotion_report)
    old_id = registry.current_release_id
    registry = registry.supersede(second.promotion_report, reason="new calibrated policy")
    new_id = registry.current_release_id
    by_id = {item.release.policy_release_id: item for item in registry.records}
    assert old_id != new_id
    assert by_id[old_id].status is PolicyReleaseStatus.SUPERSEDED
    assert by_id[old_id].successor_release_id == new_id
    assert by_id[new_id].status is PolicyReleaseStatus.ACTIVE
    assert registry.events[1].previous_event_sha256 == registry.events[0].sha256
    assert verify_policy_registry_envelope(registry.to_envelope()) == registry.canonical_payload()
    assert verify_policy_registry_full_bindings(registry, (first, second))


def test_duplicate_and_revocation_are_terminal():
    first = _binding()
    registry = PolicyRegistry.create(first.promotion_report)
    with pytest.raises(ValueError, match="own predecessor"):
        registry.supersede(first.promotion_report, reason="duplicate")
    registry = registry.revoke(reason="safety stop", evidence_sha256="1" * 64)
    assert registry.current_release_id is None
    assert registry.records[-1].status is PolicyReleaseStatus.REVOKED
    with pytest.raises(ValueError, match="revoked lineage"):
        registry.supersede(_alternate().promotion_report, reason="cannot reactivate")


def test_full_binding_requires_every_release():
    first, second = _binding(), _alternate()
    registry = PolicyRegistry.create(first.promotion_report).supersede(second.promotion_report, reason="new")
    with pytest.raises(ValueError, match="missing full upstream"):
        verify_policy_registry_full_bindings(registry, (first,))
