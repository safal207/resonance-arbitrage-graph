from copy import deepcopy
import hashlib
import json

import pytest

from resonance_arbitrage_graph.policy_authority import (
    PolicyAuthorityAction,
    PolicyAuthorityLedger,
    PolicyAuthorizationBinding,
    authorize_registry_event,
    make_policy_authority_registry_receipt,
    verify_policy_authority_ledger_envelope,
    verify_policy_authority_registry_full_binding,
    verify_policy_authorization_binding,
    verify_policy_authorization_receipt_envelope,
)
from resonance_arbitrage_graph.policy_registry import PolicyRegistry
from test_policy_registry import _alternate, _binding


def _canonical_sha(payload: dict) -> str:
    raw = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _root(registry: PolicyRegistry) -> PolicyAuthorityLedger:
    context = registry.records[0].release.policy_context_sha256
    return PolicyAuthorityLedger.bootstrap(
        authority_id="governance/root",
        authority_basis="repository governance charter",
        policy_context_sha256=context,
        actions=(
            PolicyAuthorityAction.RELEASE,
            PolicyAuthorityAction.SUPERSEDE,
            PolicyAuthorityAction.REVOKE,
        ),
        evidence_sha256="a" * 64,
    )


def test_root_and_delegated_authority_cover_registry_lineage():
    first, second = _binding(), _alternate()
    initial = PolicyRegistry.create(first.promotion_report)
    registry = initial.supersede(second.promotion_report, reason="new calibrated policy")
    root = _root(initial)
    child = root.delegate(
        parent_grant_id=root.root_grant_id,
        authority_id="governance/calibration-operator",
        authority_basis="delegated calibration promotion authority",
        actions=(PolicyAuthorityAction.SUPERSEDE,),
        evidence_sha256="b" * 64,
        reason="delegate supersession only",
    )
    child_grant = child.grants[-1]

    release_auth = authorize_registry_event(
        root,
        registry,
        grant_id=root.root_grant_id,
        registry_event_sequence=1,
        evidence_sha256="c" * 64,
    )
    supersede_auth = authorize_registry_event(
        child,
        registry,
        grant_id=child_grant.grant_id,
        registry_event_sequence=2,
        evidence_sha256="d" * 64,
    )

    assert release_auth.action is PolicyAuthorityAction.RELEASE
    assert supersede_auth.action is PolicyAuthorityAction.SUPERSEDE
    assert supersede_auth.grant_chain == (root.root_grant_id, child_grant.grant_id)
    assert verify_policy_authorization_binding(release_auth, root, registry)
    assert verify_policy_authorization_binding(supersede_auth, child, registry)

    receipt = make_policy_authority_registry_receipt(
        registry,
        (release_auth, supersede_auth),
    )
    assert verify_policy_authority_registry_full_binding(
        receipt,
        registry,
        (
            PolicyAuthorizationBinding(release_auth, root),
            PolicyAuthorizationBinding(supersede_auth, child),
        ),
    )


def test_delegation_cannot_escalate_actions_or_self_delegate():
    registry = PolicyRegistry.create(_binding().promotion_report)
    root = _root(registry)
    child = root.delegate(
        parent_grant_id=root.root_grant_id,
        authority_id="governance/operator",
        authority_basis="supersession only",
        actions=(PolicyAuthorityAction.SUPERSEDE,),
        evidence_sha256="b" * 64,
        reason="narrow delegation",
    )
    child_id = child.grants[-1].grant_id

    with pytest.raises(ValueError, match="escalate"):
        child.delegate(
            parent_grant_id=child_id,
            authority_id="governance/suboperator",
            authority_basis="attempted escalation",
            actions=(PolicyAuthorityAction.REVOKE,),
            evidence_sha256="c" * 64,
            reason="invalid",
        )

    with pytest.raises(ValueError, match="self-delegate"):
        root.delegate(
            parent_grant_id=root.root_grant_id,
            authority_id="governance/root",
            authority_basis="same identity",
            actions=(PolicyAuthorityAction.RELEASE,),
            evidence_sha256="d" * 64,
            reason="invalid",
        )


def test_grant_scope_is_exact_policy_context():
    registry = PolicyRegistry.create(_binding().promotion_report)
    wrong = PolicyAuthorityLedger.bootstrap(
        authority_id="governance/root",
        authority_basis="wrong context charter",
        policy_context_sha256="f" * 64,
        actions=(PolicyAuthorityAction.RELEASE,),
        evidence_sha256="a" * 64,
    )
    with pytest.raises(ValueError, match="policy context"):
        authorize_registry_event(
            wrong,
            registry,
            grant_id=wrong.root_grant_id,
            registry_event_sequence=1,
            evidence_sha256="c" * 64,
        )


def test_parent_revocation_blocks_descendant_future_authority_but_not_old_snapshot_receipt():
    first, second = _binding(), _alternate()
    initial = PolicyRegistry.create(first.promotion_report)
    registry = initial.supersede(second.promotion_report, reason="new calibrated policy")
    root = _root(initial)
    delegated = root.delegate(
        parent_grant_id=root.root_grant_id,
        authority_id="governance/operator",
        authority_basis="supersession only",
        actions=(PolicyAuthorityAction.SUPERSEDE,),
        evidence_sha256="b" * 64,
        reason="delegate",
    )
    child_id = delegated.grants[-1].grant_id
    old_receipt = authorize_registry_event(
        delegated,
        registry,
        grant_id=child_id,
        registry_event_sequence=2,
        evidence_sha256="c" * 64,
    )
    assert verify_policy_authorization_binding(old_receipt, delegated, registry)

    revoked = delegated.revoke_grant(
        delegated.root_grant_id,
        reason="root authority withdrawn",
        evidence_sha256="d" * 64,
    )
    assert not revoked.is_effective(child_id)
    with pytest.raises(ValueError, match="not effective"):
        authorize_registry_event(
            revoked,
            registry,
            grant_id=child_id,
            registry_event_sequence=2,
            evidence_sha256="e" * 64,
        )
    assert verify_policy_authorization_binding(old_receipt, delegated, registry)


def test_authorization_action_tamper_is_rejected_even_with_recomputed_outer_sha():
    registry = PolicyRegistry.create(_binding().promotion_report)
    root = _root(registry)
    receipt = authorize_registry_event(
        root,
        registry,
        grant_id=root.root_grant_id,
        registry_event_sequence=1,
        evidence_sha256="c" * 64,
    )
    envelope = deepcopy(receipt.to_envelope())
    envelope["payload"]["action"] = PolicyAuthorityAction.REVOKE.value
    envelope["sha256"] = _canonical_sha(envelope["payload"])
    with pytest.raises(ValueError, match="does not match registry event type"):
        verify_policy_authorization_receipt_envelope(envelope)


def test_authority_ledger_hash_chain_tamper_is_rejected():
    registry = PolicyRegistry.create(_binding().promotion_report)
    root = _root(registry)
    delegated = root.delegate(
        parent_grant_id=root.root_grant_id,
        authority_id="governance/operator",
        authority_basis="supersession only",
        actions=(PolicyAuthorityAction.SUPERSEDE,),
        evidence_sha256="b" * 64,
        reason="delegate",
    )
    envelope = deepcopy(delegated.to_envelope())
    first = envelope["payload"]["events"][0]
    first["payload"]["reason"] = "tampered root reason"
    first["sha256"] = _canonical_sha(first["payload"])
    envelope["sha256"] = _canonical_sha(envelope["payload"])
    with pytest.raises(ValueError, match="hash chain"):
        verify_policy_authority_ledger_envelope(envelope)


def test_full_registry_binding_requires_exact_event_coverage():
    first, second = _binding(), _alternate()
    initial = PolicyRegistry.create(first.promotion_report)
    registry = initial.supersede(second.promotion_report, reason="new calibrated policy")
    root = _root(initial)
    auth1 = authorize_registry_event(
        root,
        registry,
        grant_id=root.root_grant_id,
        registry_event_sequence=1,
        evidence_sha256="c" * 64,
    )
    auth2 = authorize_registry_event(
        root,
        registry,
        grant_id=root.root_grant_id,
        registry_event_sequence=2,
        evidence_sha256="d" * 64,
    )
    receipt = make_policy_authority_registry_receipt(registry, (auth1, auth2))
    with pytest.raises(ValueError, match="cover every registry event"):
        verify_policy_authority_registry_full_binding(
            receipt,
            registry,
            (PolicyAuthorizationBinding(auth1, root),),
        )
