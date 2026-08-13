from __future__ import annotations

from dataclasses import dataclass

from .policy_promotion import PolicyPromotionReport, verify_policy_promotion_bundle_binding
from .policy_registry import PolicyRegistry, PolicyRelease
from .replay import ReplayBundle
from .stability_decomposition import StabilityDecompositionReport
from .walk_forward import WalkForwardReport


@dataclass(frozen=True, slots=True)
class PolicyReleaseBinding:
    promotion_report: PolicyPromotionReport
    walk_forward_report: WalkForwardReport
    decomposition_report: StabilityDecompositionReport
    replay_bundle: ReplayBundle

    def verify(self) -> bool:
        return verify_policy_promotion_bundle_binding(
            self.promotion_report,
            self.walk_forward_report,
            self.decomposition_report,
            self.replay_bundle,
        )


def verify_policy_registry_full_bindings(
    registry: PolicyRegistry,
    bindings: tuple[PolicyReleaseBinding, ...],
) -> bool:
    by_sha: dict[str, PolicyReleaseBinding] = {}
    for binding in bindings:
        if not isinstance(binding, PolicyReleaseBinding):
            raise ValueError("registry full binding input has invalid type")
        binding.verify()
        digest = binding.promotion_report.sha256
        if digest in by_sha:
            raise ValueError("duplicate fully-bound promotion report SHA")
        by_sha[digest] = binding

    for record in registry.records:
        release = record.release
        binding = by_sha.get(release.promotion_report_sha256)
        if binding is None:
            raise ValueError("registry release is missing full upstream promotion evidence")
        rebuilt = PolicyRelease.from_promotion(
            binding.promotion_report,
            predecessor_release_id=release.predecessor_release_id,
        )
        if rebuilt != release:
            raise ValueError("registry release differs from fully-bound promotion evidence")
    return True
