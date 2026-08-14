from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from enum import Enum
import hashlib
import hmac
import json
from typing import Any

from .policy_registry import (
    PolicyRegistry,
    PolicyRegistryEvent,
    PolicyRegistryEventType,
    verify_policy_registry_envelope,
)

_GRANT_SCHEMA = "resonance.arbitrage.policy-authority-grant/v0.1"
_AUTHORITY_EVENT_SCHEMA = "resonance.arbitrage.policy-authority-event/v0.1"
_AUTHORITY_LEDGER_SCHEMA = "resonance.arbitrage.policy-authority-ledger/v0.1"
_AUTHORIZATION_SCHEMA = "resonance.arbitrage.policy-authorization-receipt/v0.1"
_AUTHORIZED_REGISTRY_SCHEMA = "resonance.arbitrage.authorized-policy-registry/v0.1"
_ZERO_SHA256 = "0" * 64
_GRANT_PREFIX = "pag_"


def _json(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def _sha(value: Any) -> str:
    return hashlib.sha256(_json(value).encode("utf-8")).hexdigest()


def _sha_ok(value: Any, name: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise ValueError(f"{name} must be a SHA-256 hex digest")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{name} must be hexadecimal") from exc
    return value


def _text(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be non-empty")
    return value.strip()


def _grant_id_ok(value: Any, name: str = "grant_id") -> str:
    if not isinstance(value, str) or not value.startswith(_GRANT_PREFIX):
        raise ValueError(f"{name} has invalid prefix")
    _sha_ok(value[len(_GRANT_PREFIX) :], name)
    return value


class PolicyAuthorityAction(str, Enum):
    RELEASE = "RELEASE"
    SUPERSEDE = "SUPERSEDE"
    REVOKE = "REVOKE"


class PolicyAuthorityEventType(str, Enum):
    ROOT_GRANTED = "ROOT_GRANTED"
    DELEGATED = "DELEGATED"
    GRANT_REVOKED = "GRANT_REVOKED"


_EVENT_ACTION = {
    PolicyRegistryEventType.RELEASED: PolicyAuthorityAction.RELEASE,
    PolicyRegistryEventType.SUPERSEDED: PolicyAuthorityAction.SUPERSEDE,
    PolicyRegistryEventType.REVOKED: PolicyAuthorityAction.REVOKE,
}


def _normalize_actions(actions: Sequence[PolicyAuthorityAction]) -> tuple[PolicyAuthorityAction, ...]:
    normalized = tuple(actions)
    if not normalized:
        raise ValueError("authority actions must be non-empty")
    if any(not isinstance(action, PolicyAuthorityAction) for action in normalized):
        raise ValueError("authority actions must use PolicyAuthorityAction values")
    if len(set(normalized)) != len(normalized):
        raise ValueError("authority actions must be unique")
    return tuple(sorted(normalized, key=lambda action: action.value))


def authority_grant_id_for(
    *,
    authority_id: str,
    authority_basis: str,
    policy_context_sha256: str,
    actions: Sequence[PolicyAuthorityAction],
    parent_grant_id: str | None,
    evidence_sha256: str,
) -> str:
    authority_id = _text(authority_id, "authority_id")
    authority_basis = _text(authority_basis, "authority_basis")
    policy_context_sha256 = _sha_ok(policy_context_sha256, "policy_context_sha256")
    evidence_sha256 = _sha_ok(evidence_sha256, "evidence_sha256")
    normalized = _normalize_actions(actions)
    if parent_grant_id is not None:
        _grant_id_ok(parent_grant_id, "parent_grant_id")
    payload = {
        "schema": _GRANT_SCHEMA,
        "authority_id": authority_id,
        "authority_basis": authority_basis,
        "policy_context_sha256": policy_context_sha256,
        "actions": [action.value for action in normalized],
        "parent_grant_id": parent_grant_id,
        "evidence_sha256": evidence_sha256,
    }
    return _GRANT_PREFIX + _sha(payload)


@dataclass(frozen=True, slots=True)
class PolicyAuthorityGrant:
    grant_id: str
    authority_id: str
    authority_basis: str
    policy_context_sha256: str
    actions: tuple[PolicyAuthorityAction, ...]
    parent_grant_id: str | None
    evidence_sha256: str

    def __post_init__(self) -> None:
        _grant_id_ok(self.grant_id)
        object.__setattr__(self, "authority_id", _text(self.authority_id, "authority_id"))
        object.__setattr__(
            self,
            "authority_basis",
            _text(self.authority_basis, "authority_basis"),
        )
        _sha_ok(self.policy_context_sha256, "policy_context_sha256")
        object.__setattr__(self, "actions", _normalize_actions(self.actions))
        if self.parent_grant_id is not None:
            _grant_id_ok(self.parent_grant_id, "parent_grant_id")
            if self.parent_grant_id == self.grant_id:
                raise ValueError("grant cannot be its own parent")
        _sha_ok(self.evidence_sha256, "evidence_sha256")
        expected = authority_grant_id_for(
            authority_id=self.authority_id,
            authority_basis=self.authority_basis,
            policy_context_sha256=self.policy_context_sha256,
            actions=self.actions,
            parent_grant_id=self.parent_grant_id,
            evidence_sha256=self.evidence_sha256,
        )
        if not hmac.compare_digest(expected, self.grant_id):
            raise ValueError("grant_id does not match authority grant identity")

    @classmethod
    def create(
        cls,
        *,
        authority_id: str,
        authority_basis: str,
        policy_context_sha256: str,
        actions: Sequence[PolicyAuthorityAction],
        parent_grant_id: str | None,
        evidence_sha256: str,
    ) -> "PolicyAuthorityGrant":
        normalized = _normalize_actions(actions)
        grant_id = authority_grant_id_for(
            authority_id=authority_id,
            authority_basis=authority_basis,
            policy_context_sha256=policy_context_sha256,
            actions=normalized,
            parent_grant_id=parent_grant_id,
            evidence_sha256=evidence_sha256,
        )
        return cls(
            grant_id,
            authority_id,
            authority_basis,
            policy_context_sha256,
            normalized,
            parent_grant_id,
            evidence_sha256,
        )

    def to_payload(self) -> dict[str, Any]:
        return {
            "grant_id": self.grant_id,
            "authority_id": self.authority_id,
            "authority_basis": self.authority_basis,
            "policy_context_sha256": self.policy_context_sha256,
            "actions": [action.value for action in self.actions],
            "parent_grant_id": self.parent_grant_id,
            "evidence_sha256": self.evidence_sha256,
        }


@dataclass(frozen=True, slots=True)
class PolicyAuthorityEvent:
    sequence: int
    event_type: PolicyAuthorityEventType
    previous_event_sha256: str
    target_grant_id: str | None
    grant: PolicyAuthorityGrant | None
    reason: str
    evidence_sha256: str

    def __post_init__(self) -> None:
        if isinstance(self.sequence, bool) or not isinstance(self.sequence, int) or self.sequence < 1:
            raise ValueError("authority event sequence must be an integer >= 1")
        if not isinstance(self.event_type, PolicyAuthorityEventType):
            raise ValueError("invalid authority event type")
        _sha_ok(self.previous_event_sha256, "previous_event_sha256")
        if self.target_grant_id is not None:
            _grant_id_ok(self.target_grant_id, "target_grant_id")
        _text(self.reason, "reason")
        _sha_ok(self.evidence_sha256, "evidence_sha256")

        if self.event_type is PolicyAuthorityEventType.ROOT_GRANTED:
            if self.grant is None or self.target_grant_id is not None:
                raise ValueError("ROOT_GRANTED requires a root grant and no target")
            if self.grant.parent_grant_id is not None:
                raise ValueError("root authority grant cannot have a parent")
            if self.evidence_sha256 != self.grant.evidence_sha256:
                raise ValueError("root grant event evidence must equal grant evidence")
        elif self.event_type is PolicyAuthorityEventType.DELEGATED:
            if self.grant is None or self.target_grant_id is None:
                raise ValueError("DELEGATED requires a parent target and child grant")
            if self.grant.parent_grant_id != self.target_grant_id:
                raise ValueError("delegated grant parent must equal event target")
            if self.evidence_sha256 != self.grant.evidence_sha256:
                raise ValueError("delegation event evidence must equal grant evidence")
        elif self.grant is not None or self.target_grant_id is None:
            raise ValueError("GRANT_REVOKED requires a target and no new grant")

    def canonical_payload(self) -> dict[str, Any]:
        return {
            "schema": _AUTHORITY_EVENT_SCHEMA,
            "sequence": self.sequence,
            "event_type": self.event_type.value,
            "previous_event_sha256": self.previous_event_sha256,
            "target_grant_id": self.target_grant_id,
            "grant": self.grant.to_payload() if self.grant else None,
            "reason": self.reason,
            "evidence_sha256": self.evidence_sha256,
        }

    @property
    def sha256(self) -> str:
        return _sha(self.canonical_payload())

    def to_envelope(self) -> dict[str, Any]:
        return {"payload": self.canonical_payload(), "sha256": self.sha256}


def _authority_state(
    events: Sequence[PolicyAuthorityEvent],
) -> tuple[dict[str, PolicyAuthorityGrant], set[str], str]:
    grants: dict[str, PolicyAuthorityGrant] = {}
    revoked: set[str] = set()
    root_grant_id = ""

    def effective(grant_id: str) -> bool:
        cursor = grant_id
        seen: set[str] = set()
        while True:
            if cursor in seen:
                raise ValueError("authority grant cycle detected")
            seen.add(cursor)
            if cursor in revoked:
                return False
            grant = grants[cursor]
            if grant.parent_grant_id is None:
                return True
            cursor = grant.parent_grant_id

    def chain_authorities(grant_id: str) -> tuple[str, ...]:
        values: list[str] = []
        cursor = grant_id
        while True:
            grant = grants[cursor]
            values.append(grant.authority_id)
            if grant.parent_grant_id is None:
                break
            cursor = grant.parent_grant_id
        return tuple(reversed(values))

    for index, event in enumerate(events, start=1):
        if event.sequence != index:
            raise ValueError("authority event sequences must be contiguous")
        previous = _ZERO_SHA256 if index == 1 else events[index - 2].sha256
        if not hmac.compare_digest(previous, event.previous_event_sha256):
            raise ValueError("authority event hash chain is broken")

        if event.event_type is PolicyAuthorityEventType.ROOT_GRANTED:
            if index != 1 or grants:
                raise ValueError("ROOT_GRANTED is only valid as first authority event")
            grant = event.grant
            assert grant is not None
            grants[grant.grant_id] = grant
            root_grant_id = grant.grant_id
            continue

        if not grants:
            raise ValueError("authority ledger is missing root grant")

        if event.event_type is PolicyAuthorityEventType.DELEGATED:
            grant = event.grant
            assert grant is not None
            parent_id = event.target_grant_id
            assert parent_id is not None
            parent = grants.get(parent_id)
            if parent is None:
                raise ValueError("delegation parent grant is unknown")
            if not effective(parent_id):
                raise ValueError("delegation parent grant is not effective")
            if grant.grant_id in grants:
                raise ValueError("duplicate authority grant_id")
            if grant.policy_context_sha256 != parent.policy_context_sha256:
                raise ValueError("delegation cannot broaden policy context scope")
            if not set(grant.actions).issubset(parent.actions):
                raise ValueError("delegation cannot escalate authority actions")
            if grant.authority_id == parent.authority_id:
                raise ValueError("authority cannot self-delegate")
            if grant.authority_id in chain_authorities(parent_id):
                raise ValueError("delegation would repeat an ancestor authority identity")
            grants[grant.grant_id] = grant
            continue

        target = event.target_grant_id
        assert target is not None
        if target not in grants:
            raise ValueError("revoked authority grant is unknown")
        if target in revoked:
            raise ValueError("authority grant is already revoked")
        revoked.add(target)

    if not grants or not root_grant_id:
        raise ValueError("authority ledger requires a root grant")
    return grants, revoked, root_grant_id


@dataclass(frozen=True, slots=True)
class PolicyAuthorityLedger:
    events: tuple[PolicyAuthorityEvent, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "events", tuple(self.events))
        if not self.events:
            raise ValueError("authority ledger requires at least one event")
        _authority_state(self.events)

    @classmethod
    def bootstrap(
        cls,
        *,
        authority_id: str,
        authority_basis: str,
        policy_context_sha256: str,
        actions: Sequence[PolicyAuthorityAction],
        evidence_sha256: str,
        reason: str = "bootstrap root policy authority",
    ) -> "PolicyAuthorityLedger":
        grant = PolicyAuthorityGrant.create(
            authority_id=authority_id,
            authority_basis=authority_basis,
            policy_context_sha256=policy_context_sha256,
            actions=actions,
            parent_grant_id=None,
            evidence_sha256=evidence_sha256,
        )
        event = PolicyAuthorityEvent(
            1,
            PolicyAuthorityEventType.ROOT_GRANTED,
            _ZERO_SHA256,
            None,
            grant,
            _text(reason, "reason"),
            grant.evidence_sha256,
        )
        return cls((event,))

    @property
    def grants(self) -> tuple[PolicyAuthorityGrant, ...]:
        grants, _, _ = _authority_state(self.events)
        return tuple(grants.values())

    @property
    def root_grant_id(self) -> str:
        return _authority_state(self.events)[2]

    def grant(self, grant_id: str) -> PolicyAuthorityGrant:
        _grant_id_ok(grant_id)
        grants, _, _ = _authority_state(self.events)
        try:
            return grants[grant_id]
        except KeyError as exc:
            raise ValueError("authority grant is unknown") from exc

    def is_effective(self, grant_id: str) -> bool:
        grant = self.grant(grant_id)
        grants, revoked, _ = _authority_state(self.events)
        cursor = grant.grant_id
        seen: set[str] = set()
        while True:
            if cursor in seen:
                raise ValueError("authority grant cycle detected")
            seen.add(cursor)
            if cursor in revoked:
                return False
            current = grants[cursor]
            if current.parent_grant_id is None:
                return True
            cursor = current.parent_grant_id

    def grant_chain(self, grant_id: str) -> tuple[PolicyAuthorityGrant, ...]:
        grant = self.grant(grant_id)
        grants, _, _ = _authority_state(self.events)
        chain: list[PolicyAuthorityGrant] = []
        cursor = grant
        while True:
            chain.append(cursor)
            if cursor.parent_grant_id is None:
                break
            cursor = grants[cursor.parent_grant_id]
        return tuple(reversed(chain))

    def delegate(
        self,
        *,
        parent_grant_id: str,
        authority_id: str,
        authority_basis: str,
        actions: Sequence[PolicyAuthorityAction],
        evidence_sha256: str,
        reason: str,
    ) -> "PolicyAuthorityLedger":
        parent = self.grant(parent_grant_id)
        if not self.is_effective(parent_grant_id):
            raise ValueError("delegation parent grant is not effective")
        grant = PolicyAuthorityGrant.create(
            authority_id=authority_id,
            authority_basis=authority_basis,
            policy_context_sha256=parent.policy_context_sha256,
            actions=actions,
            parent_grant_id=parent.grant_id,
            evidence_sha256=evidence_sha256,
        )
        event = PolicyAuthorityEvent(
            len(self.events) + 1,
            PolicyAuthorityEventType.DELEGATED,
            self.events[-1].sha256,
            parent.grant_id,
            grant,
            _text(reason, "reason"),
            grant.evidence_sha256,
        )
        return PolicyAuthorityLedger(self.events + (event,))

    def revoke_grant(
        self,
        grant_id: str,
        *,
        reason: str,
        evidence_sha256: str,
    ) -> "PolicyAuthorityLedger":
        self.grant(grant_id)
        _, revoked, _ = _authority_state(self.events)
        if grant_id in revoked:
            raise ValueError("authority grant is already revoked")
        event = PolicyAuthorityEvent(
            len(self.events) + 1,
            PolicyAuthorityEventType.GRANT_REVOKED,
            self.events[-1].sha256,
            grant_id,
            None,
            _text(reason, "reason"),
            _sha_ok(evidence_sha256, "evidence_sha256"),
        )
        return PolicyAuthorityLedger(self.events + (event,))

    def canonical_payload(self) -> dict[str, Any]:
        grants, revoked, root = _authority_state(self.events)
        effective = tuple(sorted(grant_id for grant_id in grants if self.is_effective(grant_id)))
        return {
            "schema": _AUTHORITY_LEDGER_SCHEMA,
            "events": [event.to_envelope() for event in self.events],
            "grants": [grants[grant_id].to_payload() for grant_id in sorted(grants)],
            "root_grant_id": root,
            "direct_revoked_grant_ids": sorted(revoked),
            "effective_grant_ids": list(effective),
            "delegation_only_reduces_authority": True,
            "revocation_is_forward_only": True,
            "authority_id_is_not_identity_proof": True,
            "paper_policy_only": True,
        }

    @property
    def sha256(self) -> str:
        return _sha(self.canonical_payload())

    def to_envelope(self) -> dict[str, Any]:
        return {"payload": self.canonical_payload(), "sha256": self.sha256}

    @classmethod
    def from_envelope(cls, envelope: Mapping[str, Any]) -> "PolicyAuthorityLedger":
        verify_policy_authority_ledger_envelope(envelope)
        return cls(tuple(_authority_event_from_envelope(item) for item in envelope["payload"]["events"]))


def _grant_from_payload(payload: Any) -> PolicyAuthorityGrant:
    keys = {
        "grant_id",
        "authority_id",
        "authority_basis",
        "policy_context_sha256",
        "actions",
        "parent_grant_id",
        "evidence_sha256",
    }
    if not isinstance(payload, Mapping) or set(payload) != keys:
        raise ValueError("authority grant payload is not canonical")
    actions = payload["actions"]
    if not isinstance(actions, list) or not actions:
        raise ValueError("authority grant actions payload is invalid")
    try:
        parsed_actions = tuple(PolicyAuthorityAction(value) for value in actions)
    except (TypeError, ValueError) as exc:
        raise ValueError("authority grant action is invalid") from exc
    return PolicyAuthorityGrant(
        payload["grant_id"],
        payload["authority_id"],
        payload["authority_basis"],
        payload["policy_context_sha256"],
        parsed_actions,
        payload["parent_grant_id"],
        payload["evidence_sha256"],
    )


def _authority_event_from_envelope(envelope: Any) -> PolicyAuthorityEvent:
    if not isinstance(envelope, Mapping) or set(envelope) != {"payload", "sha256"}:
        raise ValueError("authority event envelope is not canonical")
    payload = envelope["payload"]
    digest = _sha_ok(envelope["sha256"], "authority_event_sha256")
    keys = {
        "schema",
        "sequence",
        "event_type",
        "previous_event_sha256",
        "target_grant_id",
        "grant",
        "reason",
        "evidence_sha256",
    }
    if not isinstance(payload, Mapping) or set(payload) != keys or payload.get("schema") != _AUTHORITY_EVENT_SCHEMA:
        raise ValueError("authority event payload is not canonical")
    try:
        event_type = PolicyAuthorityEventType(payload["event_type"])
    except (TypeError, ValueError) as exc:
        raise ValueError("authority event type is invalid") from exc
    event = PolicyAuthorityEvent(
        payload["sequence"],
        event_type,
        payload["previous_event_sha256"],
        payload["target_grant_id"],
        None if payload["grant"] is None else _grant_from_payload(payload["grant"]),
        payload["reason"],
        payload["evidence_sha256"],
    )
    if not hmac.compare_digest(event.sha256, digest):
        raise ValueError("authority event SHA-256 does not match payload")
    return event


def verify_policy_authority_ledger_envelope(envelope: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(envelope, Mapping) or set(envelope) != {"payload", "sha256"}:
        raise ValueError("authority ledger envelope is not canonical")
    payload = envelope["payload"]
    digest = _sha_ok(envelope["sha256"], "authority_ledger_sha256")
    keys = {
        "schema",
        "events",
        "grants",
        "root_grant_id",
        "direct_revoked_grant_ids",
        "effective_grant_ids",
        "delegation_only_reduces_authority",
        "revocation_is_forward_only",
        "authority_id_is_not_identity_proof",
        "paper_policy_only",
    }
    if not isinstance(payload, dict) or set(payload) != keys or payload.get("schema") != _AUTHORITY_LEDGER_SCHEMA:
        raise ValueError("authority ledger payload is not canonical")
    for flag in (
        "delegation_only_reduces_authority",
        "revocation_is_forward_only",
        "authority_id_is_not_identity_proof",
        "paper_policy_only",
    ):
        if payload.get(flag) is not True:
            raise ValueError(f"authority ledger invariant flag is invalid: {flag}")
    events = payload.get("events")
    if not isinstance(events, list) or not events:
        raise ValueError("authority ledger events must be a non-empty list")
    rebuilt = PolicyAuthorityLedger(tuple(_authority_event_from_envelope(item) for item in events)).canonical_payload()
    if rebuilt != payload:
        raise ValueError("authority ledger snapshot does not match event history")
    if not hmac.compare_digest(_sha(payload), digest):
        raise ValueError("authority ledger SHA-256 does not match payload")
    _json(payload)
    return dict(payload)


def _registry_event_context(registry: PolicyRegistry, event: PolicyRegistryEvent) -> str:
    if event.release is not None:
        return event.release.policy_context_sha256
    target = event.target_release_id
    if target is None:
        raise ValueError("registry event lacks policy context source")
    for record in registry.records:
        if record.release.policy_release_id == target:
            return record.release.policy_context_sha256
    raise ValueError("registry event target release is unknown")


@dataclass(frozen=True, slots=True)
class PolicyAuthorizationReceipt:
    authority_ledger_sha256: str
    grant_id: str
    grant_chain: tuple[str, ...]
    authority_id: str
    action: PolicyAuthorityAction
    policy_context_sha256: str
    registry_event_sequence: int
    registry_event_sha256: str
    registry_event_type: PolicyRegistryEventType
    evidence_sha256: str

    def __post_init__(self) -> None:
        _sha_ok(self.authority_ledger_sha256, "authority_ledger_sha256")
        _grant_id_ok(self.grant_id)
        object.__setattr__(self, "grant_chain", tuple(self.grant_chain))
        if not self.grant_chain or self.grant_chain[-1] != self.grant_id:
            raise ValueError("authorization grant chain must end at grant_id")
        if len(set(self.grant_chain)) != len(self.grant_chain):
            raise ValueError("authorization grant chain must be unique")
        for grant_id in self.grant_chain:
            _grant_id_ok(grant_id, "grant_chain item")
        object.__setattr__(self, "authority_id", _text(self.authority_id, "authority_id"))
        if not isinstance(self.action, PolicyAuthorityAction):
            raise ValueError("authorization action has invalid type")
        _sha_ok(self.policy_context_sha256, "policy_context_sha256")
        if isinstance(self.registry_event_sequence, bool) or not isinstance(self.registry_event_sequence, int) or self.registry_event_sequence < 1:
            raise ValueError("registry_event_sequence must be an integer >= 1")
        _sha_ok(self.registry_event_sha256, "registry_event_sha256")
        if not isinstance(self.registry_event_type, PolicyRegistryEventType):
            raise ValueError("registry_event_type has invalid type")
        if _EVENT_ACTION[self.registry_event_type] is not self.action:
            raise ValueError("authorization action does not match registry event type")
        _sha_ok(self.evidence_sha256, "evidence_sha256")

    def canonical_payload(self) -> dict[str, Any]:
        return {
            "schema": _AUTHORIZATION_SCHEMA,
            "authority_ledger_sha256": self.authority_ledger_sha256,
            "grant_id": self.grant_id,
            "grant_chain": list(self.grant_chain),
            "authority_id": self.authority_id,
            "action": self.action.value,
            "policy_context_sha256": self.policy_context_sha256,
            "registry_event_sequence": self.registry_event_sequence,
            "registry_event_sha256": self.registry_event_sha256,
            "registry_event_type": self.registry_event_type.value,
            "evidence_sha256": self.evidence_sha256,
            "authorization_is_event_bound": True,
            "authority_id_is_not_identity_proof": True,
            "paper_policy_only": True,
        }

    @property
    def sha256(self) -> str:
        return _sha(self.canonical_payload())

    def to_envelope(self) -> dict[str, Any]:
        return {"payload": self.canonical_payload(), "sha256": self.sha256}

    @classmethod
    def from_envelope(cls, envelope: Mapping[str, Any]) -> "PolicyAuthorizationReceipt":
        payload = verify_policy_authorization_receipt_envelope(envelope)
        return _authorization_from_payload(payload)


def authorize_registry_event(
    ledger: PolicyAuthorityLedger,
    registry: PolicyRegistry,
    *,
    grant_id: str,
    registry_event_sequence: int,
    evidence_sha256: str,
) -> PolicyAuthorizationReceipt:
    if not isinstance(ledger, PolicyAuthorityLedger):
        raise ValueError("ledger must be PolicyAuthorityLedger")
    if not isinstance(registry, PolicyRegistry):
        raise ValueError("registry must be PolicyRegistry")
    if isinstance(registry_event_sequence, bool) or not isinstance(registry_event_sequence, int):
        raise ValueError("registry_event_sequence must be an integer")
    if registry_event_sequence < 1 or registry_event_sequence > len(registry.events):
        raise ValueError("registry_event_sequence is out of range")
    grant = ledger.grant(grant_id)
    if not ledger.is_effective(grant_id):
        raise ValueError("authority grant is not effective in bound ledger snapshot")
    event = registry.events[registry_event_sequence - 1]
    action = _EVENT_ACTION[event.event_type]
    context = _registry_event_context(registry, event)
    if context != grant.policy_context_sha256:
        raise ValueError("authority grant policy context does not match registry event")
    if action not in grant.actions:
        raise ValueError("authority grant does not permit registry event action")
    chain = ledger.grant_chain(grant_id)
    return PolicyAuthorizationReceipt(
        ledger.sha256,
        grant.grant_id,
        tuple(item.grant_id for item in chain),
        grant.authority_id,
        action,
        context,
        event.sequence,
        event.sha256,
        event.event_type,
        _sha_ok(evidence_sha256, "evidence_sha256"),
    )


def _authorization_from_payload(payload: Mapping[str, Any]) -> PolicyAuthorizationReceipt:
    try:
        action = PolicyAuthorityAction(payload["action"])
        event_type = PolicyRegistryEventType(payload["registry_event_type"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("authorization enum payload is invalid") from exc
    grant_chain = payload.get("grant_chain")
    if not isinstance(grant_chain, list):
        raise ValueError("authorization grant_chain must be a list")
    return PolicyAuthorizationReceipt(
        payload["authority_ledger_sha256"],
        payload["grant_id"],
        tuple(grant_chain),
        payload["authority_id"],
        action,
        payload["policy_context_sha256"],
        payload["registry_event_sequence"],
        payload["registry_event_sha256"],
        event_type,
        payload["evidence_sha256"],
    )


def verify_policy_authorization_receipt_envelope(envelope: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(envelope, Mapping) or set(envelope) != {"payload", "sha256"}:
        raise ValueError("authorization envelope is not canonical")
    payload = envelope["payload"]
    digest = _sha_ok(envelope["sha256"], "authorization_sha256")
    keys = {
        "schema",
        "authority_ledger_sha256",
        "grant_id",
        "grant_chain",
        "authority_id",
        "action",
        "policy_context_sha256",
        "registry_event_sequence",
        "registry_event_sha256",
        "registry_event_type",
        "evidence_sha256",
        "authorization_is_event_bound",
        "authority_id_is_not_identity_proof",
        "paper_policy_only",
    }
    if not isinstance(payload, dict) or set(payload) != keys or payload.get("schema") != _AUTHORIZATION_SCHEMA:
        raise ValueError("authorization payload is not canonical")
    for flag in (
        "authorization_is_event_bound",
        "authority_id_is_not_identity_proof",
        "paper_policy_only",
    ):
        if payload.get(flag) is not True:
            raise ValueError(f"authorization invariant flag is invalid: {flag}")
    receipt = _authorization_from_payload(payload)
    if receipt.canonical_payload() != payload:
        raise ValueError("authorization payload is not canonical after reconstruction")
    if not hmac.compare_digest(receipt.sha256, digest):
        raise ValueError("authorization SHA-256 does not match payload")
    return dict(payload)


def verify_policy_authorization_binding(
    authorization: PolicyAuthorizationReceipt | Mapping[str, Any],
    ledger: PolicyAuthorityLedger | Mapping[str, Any],
    registry: PolicyRegistry | Mapping[str, Any],
) -> bool:
    receipt = (
        authorization
        if isinstance(authorization, PolicyAuthorizationReceipt)
        else PolicyAuthorizationReceipt.from_envelope(authorization)
    )
    bound_ledger = (
        ledger
        if isinstance(ledger, PolicyAuthorityLedger)
        else PolicyAuthorityLedger.from_envelope(ledger)
    )
    bound_registry = (
        registry
        if isinstance(registry, PolicyRegistry)
        else PolicyRegistry.from_envelope(registry)
    )
    if not hmac.compare_digest(receipt.authority_ledger_sha256, bound_ledger.sha256):
        raise ValueError("authorization does not bind supplied authority ledger snapshot")
    rebuilt = authorize_registry_event(
        bound_ledger,
        bound_registry,
        grant_id=receipt.grant_id,
        registry_event_sequence=receipt.registry_event_sequence,
        evidence_sha256=receipt.evidence_sha256,
    )
    if rebuilt != receipt:
        raise ValueError("authorization does not reproduce from ledger and registry event")
    return True


@dataclass(frozen=True, slots=True)
class PolicyAuthorizationBinding:
    authorization: PolicyAuthorizationReceipt
    authority_ledger: PolicyAuthorityLedger

    def verify(self, registry: PolicyRegistry) -> bool:
        return verify_policy_authorization_binding(
            self.authorization,
            self.authority_ledger,
            registry,
        )


@dataclass(frozen=True, slots=True)
class PolicyAuthorityRegistryReceipt:
    policy_registry_sha256: str
    event_sequences: tuple[int, ...]
    registry_event_sha256s: tuple[str, ...]
    authorization_sha256s: tuple[str, ...]

    def __post_init__(self) -> None:
        _sha_ok(self.policy_registry_sha256, "policy_registry_sha256")
        object.__setattr__(self, "event_sequences", tuple(self.event_sequences))
        object.__setattr__(self, "registry_event_sha256s", tuple(self.registry_event_sha256s))
        object.__setattr__(self, "authorization_sha256s", tuple(self.authorization_sha256s))
        if not self.event_sequences:
            raise ValueError("authorized registry receipt requires event coverage")
        if self.event_sequences != tuple(range(1, len(self.event_sequences) + 1)):
            raise ValueError("authorized registry event coverage must be contiguous from 1")
        if len(self.registry_event_sha256s) != len(self.event_sequences) or len(self.authorization_sha256s) != len(self.event_sequences):
            raise ValueError("authorized registry receipt arrays must have equal length")
        if len(set(self.authorization_sha256s)) != len(self.authorization_sha256s):
            raise ValueError("authorization receipts must be unique")
        for digest in self.registry_event_sha256s:
            _sha_ok(digest, "registry_event_sha256")
        for digest in self.authorization_sha256s:
            _sha_ok(digest, "authorization_sha256")

    def canonical_payload(self) -> dict[str, Any]:
        return {
            "schema": _AUTHORIZED_REGISTRY_SCHEMA,
            "policy_registry_sha256": self.policy_registry_sha256,
            "event_sequences": list(self.event_sequences),
            "registry_event_sha256s": list(self.registry_event_sha256s),
            "authorization_sha256s": list(self.authorization_sha256s),
            "all_registry_events_authorized": True,
            "authority_evidence_is_snapshot_bound": True,
            "paper_policy_only": True,
        }

    @property
    def sha256(self) -> str:
        return _sha(self.canonical_payload())

    def to_envelope(self) -> dict[str, Any]:
        return {"payload": self.canonical_payload(), "sha256": self.sha256}


def make_policy_authority_registry_receipt(
    registry: PolicyRegistry,
    authorizations: Sequence[PolicyAuthorizationReceipt],
) -> PolicyAuthorityRegistryReceipt:
    if not isinstance(registry, PolicyRegistry):
        raise ValueError("registry must be PolicyRegistry")
    receipts = tuple(authorizations)
    if len(receipts) != len(registry.events):
        raise ValueError("every registry event requires exactly one authorization receipt")
    by_sequence: dict[int, PolicyAuthorizationReceipt] = {}
    for receipt in receipts:
        if not isinstance(receipt, PolicyAuthorizationReceipt):
            raise ValueError("authorization receipt has invalid type")
        if receipt.registry_event_sequence in by_sequence:
            raise ValueError("duplicate authorization for registry event sequence")
        by_sequence[receipt.registry_event_sequence] = receipt
    ordered = tuple(by_sequence[index] for index in range(1, len(registry.events) + 1))
    for event, receipt in zip(registry.events, ordered, strict=True):
        if receipt.registry_event_sha256 != event.sha256:
            raise ValueError("authorization receipt binds wrong registry event SHA")
        if receipt.registry_event_type is not event.event_type:
            raise ValueError("authorization receipt binds wrong registry event type")
    return PolicyAuthorityRegistryReceipt(
        registry.sha256,
        tuple(event.sequence for event in registry.events),
        tuple(event.sha256 for event in registry.events),
        tuple(receipt.sha256 for receipt in ordered),
    )


def _authorized_registry_from_payload(payload: Mapping[str, Any]) -> PolicyAuthorityRegistryReceipt:
    sequences = payload.get("event_sequences")
    event_shas = payload.get("registry_event_sha256s")
    authorization_shas = payload.get("authorization_sha256s")
    if not isinstance(sequences, list) or not isinstance(event_shas, list) or not isinstance(authorization_shas, list):
        raise ValueError("authorized registry receipt arrays are invalid")
    return PolicyAuthorityRegistryReceipt(
        payload["policy_registry_sha256"],
        tuple(sequences),
        tuple(event_shas),
        tuple(authorization_shas),
    )


def verify_policy_authority_registry_receipt_envelope(envelope: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(envelope, Mapping) or set(envelope) != {"payload", "sha256"}:
        raise ValueError("authorized registry envelope is not canonical")
    payload = envelope["payload"]
    digest = _sha_ok(envelope["sha256"], "authorized_registry_sha256")
    keys = {
        "schema",
        "policy_registry_sha256",
        "event_sequences",
        "registry_event_sha256s",
        "authorization_sha256s",
        "all_registry_events_authorized",
        "authority_evidence_is_snapshot_bound",
        "paper_policy_only",
    }
    if not isinstance(payload, dict) or set(payload) != keys or payload.get("schema") != _AUTHORIZED_REGISTRY_SCHEMA:
        raise ValueError("authorized registry payload is not canonical")
    for flag in (
        "all_registry_events_authorized",
        "authority_evidence_is_snapshot_bound",
        "paper_policy_only",
    ):
        if payload.get(flag) is not True:
            raise ValueError(f"authorized registry invariant flag is invalid: {flag}")
    receipt = _authorized_registry_from_payload(payload)
    if receipt.canonical_payload() != payload:
        raise ValueError("authorized registry payload is not canonical after reconstruction")
    if not hmac.compare_digest(receipt.sha256, digest):
        raise ValueError("authorized registry SHA-256 does not match payload")
    return dict(payload)


def verify_policy_authority_registry_full_binding(
    receipt: PolicyAuthorityRegistryReceipt | Mapping[str, Any],
    registry: PolicyRegistry | Mapping[str, Any],
    bindings: Sequence[PolicyAuthorizationBinding],
) -> bool:
    authority_receipt = (
        receipt
        if isinstance(receipt, PolicyAuthorityRegistryReceipt)
        else _authorized_registry_from_payload(
            verify_policy_authority_registry_receipt_envelope(receipt)
        )
    )
    bound_registry = (
        registry
        if isinstance(registry, PolicyRegistry)
        else PolicyRegistry.from_envelope(registry)
    )
    if authority_receipt.policy_registry_sha256 != bound_registry.sha256:
        raise ValueError("authorized registry receipt does not bind supplied registry")
    supplied = tuple(bindings)
    if len(supplied) != len(bound_registry.events):
        raise ValueError("full authority binding must cover every registry event exactly once")
    by_sequence: dict[int, PolicyAuthorizationBinding] = {}
    for binding in supplied:
        if not isinstance(binding, PolicyAuthorizationBinding):
            raise ValueError("full authority binding input has invalid type")
        sequence = binding.authorization.registry_event_sequence
        if sequence in by_sequence:
            raise ValueError("duplicate full authority binding for registry event")
        binding.verify(bound_registry)
        by_sequence[sequence] = binding
    try:
        ordered = tuple(by_sequence[index] for index in range(1, len(bound_registry.events) + 1))
    except KeyError as exc:
        raise ValueError("full authority binding is missing registry event") from exc
    rebuilt = make_policy_authority_registry_receipt(
        bound_registry,
        tuple(binding.authorization for binding in ordered),
    )
    if rebuilt != authority_receipt:
        raise ValueError("authorized registry receipt does not reproduce from full bindings")
    return True
