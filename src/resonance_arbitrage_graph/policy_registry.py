from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from enum import Enum
import hashlib
import hmac
import json
from typing import Any

from .joint_holdout import JointPolicyCandidate
from .policy_promotion import PolicyPromotionReport, PolicyPromotionStatus, verify_policy_promotion_report_envelope

_RELEASE_SCHEMA = "resonance.arbitrage.policy-release-identity/v0.1"
_EVENT_SCHEMA = "resonance.arbitrage.policy-registry-event/v0.1"
_REGISTRY_SCHEMA = "resonance.arbitrage.policy-registry/v0.1"
_ZERO_SHA256 = "0" * 64
_PREFIX = "prl_"


def _json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def _sha(value: Any) -> str:
    return hashlib.sha256(_json(value).encode()).hexdigest()


def _sha_ok(value: Any, name: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise ValueError(f"{name} must be a SHA-256 hex digest")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ValueError(f"{name} must be hexadecimal") from exc
    return value


def _rid_ok(value: Any, name: str = "policy_release_id") -> str:
    if not isinstance(value, str) or not value.startswith(_PREFIX):
        raise ValueError(f"{name} has invalid prefix")
    _sha_ok(value[len(_PREFIX):], name)
    return value


def _text(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be non-empty")
    return value.strip()


def _envelope(promotion: PolicyPromotionReport | Mapping[str, Any]) -> Mapping[str, Any]:
    if isinstance(promotion, PolicyPromotionReport):
        return promotion.to_envelope()
    if not isinstance(promotion, Mapping):
        raise ValueError("promotion must be a report or envelope")
    return promotion


def _promoted(promotion: PolicyPromotionReport | Mapping[str, Any]) -> tuple[dict[str, Any], str]:
    envelope = _envelope(promotion)
    payload = verify_policy_promotion_report_envelope(envelope)
    digest = _sha_ok(envelope.get("sha256"), "promotion_report_sha256")
    decision = payload.get("decision")
    if not isinstance(decision, dict) or decision.get("status") != PolicyPromotionStatus.PROMOTED.value:
        raise ValueError("policy release requires a PROMOTED receipt")
    candidate = decision.get("candidate")
    if not isinstance(candidate, dict) or set(candidate) != {"execute_net_edge_bps", "volatile_return_bps"}:
        raise ValueError("promoted candidate is invalid")
    return payload, digest


def policy_release_id_for(*, promotion_report_sha256: str, policy_context_sha256: str, candidate: JointPolicyCandidate) -> str:
    _sha_ok(promotion_report_sha256, "promotion_report_sha256")
    _sha_ok(policy_context_sha256, "policy_context_sha256")
    if not isinstance(candidate, JointPolicyCandidate):
        raise ValueError("candidate must be JointPolicyCandidate")
    identity = {
        "schema": _RELEASE_SCHEMA,
        "promotion_report_sha256": promotion_report_sha256,
        "policy_context_sha256": policy_context_sha256,
        "candidate": candidate.to_payload(),
    }
    return _PREFIX + _sha(identity)


class PolicyReleaseStatus(str, Enum):
    ACTIVE = "ACTIVE"
    SUPERSEDED = "SUPERSEDED"
    REVOKED = "REVOKED"


class PolicyRegistryEventType(str, Enum):
    RELEASED = "RELEASED"
    SUPERSEDED = "SUPERSEDED"
    REVOKED = "REVOKED"


@dataclass(frozen=True, slots=True)
class PolicyRelease:
    policy_release_id: str
    promotion_report_sha256: str
    policy_context_sha256: str
    candidate: JointPolicyCandidate
    predecessor_release_id: str | None = None

    def __post_init__(self) -> None:
        _rid_ok(self.policy_release_id)
        _sha_ok(self.promotion_report_sha256, "promotion_report_sha256")
        _sha_ok(self.policy_context_sha256, "policy_context_sha256")
        if self.predecessor_release_id is not None:
            _rid_ok(self.predecessor_release_id, "predecessor_release_id")
            if self.predecessor_release_id == self.policy_release_id:
                raise ValueError("release cannot be its own predecessor")
        expected = policy_release_id_for(
            promotion_report_sha256=self.promotion_report_sha256,
            policy_context_sha256=self.policy_context_sha256,
            candidate=self.candidate,
        )
        if not hmac.compare_digest(expected, self.policy_release_id):
            raise ValueError("policy_release_id does not match release identity")

    @classmethod
    def from_promotion(cls, promotion: PolicyPromotionReport | Mapping[str, Any], *, predecessor_release_id: str | None = None) -> "PolicyRelease":
        payload, promotion_sha = _promoted(promotion)
        context_sha = _sha_ok(payload.get("policy_context_sha256"), "policy_context_sha256")
        candidate = JointPolicyCandidate(**payload["decision"]["candidate"])
        return cls(
            policy_release_id_for(promotion_report_sha256=promotion_sha, policy_context_sha256=context_sha, candidate=candidate),
            promotion_sha,
            context_sha,
            candidate,
            predecessor_release_id,
        )

    def to_payload(self) -> dict[str, Any]:
        return {
            "policy_release_id": self.policy_release_id,
            "promotion_report_sha256": self.promotion_report_sha256,
            "policy_context_sha256": self.policy_context_sha256,
            "candidate": self.candidate.to_payload(),
            "predecessor_release_id": self.predecessor_release_id,
        }


@dataclass(frozen=True, slots=True)
class PolicyRegistryEvent:
    sequence: int
    event_type: PolicyRegistryEventType
    previous_event_sha256: str
    target_release_id: str | None
    release: PolicyRelease | None
    reason: str
    evidence_sha256: str

    def __post_init__(self) -> None:
        if isinstance(self.sequence, bool) or not isinstance(self.sequence, int) or self.sequence < 1:
            raise ValueError("event sequence must be an integer >= 1")
        if not isinstance(self.event_type, PolicyRegistryEventType):
            raise ValueError("invalid registry event type")
        _sha_ok(self.previous_event_sha256, "previous_event_sha256")
        _sha_ok(self.evidence_sha256, "evidence_sha256")
        _text(self.reason, "reason")
        if self.target_release_id is not None:
            _rid_ok(self.target_release_id, "target_release_id")
        if self.event_type is PolicyRegistryEventType.RELEASED:
            if self.release is None or self.target_release_id is not None:
                raise ValueError("RELEASED requires release and no target")
            if self.evidence_sha256 != self.release.promotion_report_sha256:
                raise ValueError("RELEASED evidence must equal promotion receipt SHA")
        elif self.event_type is PolicyRegistryEventType.SUPERSEDED:
            if self.release is None or self.target_release_id is None:
                raise ValueError("SUPERSEDED requires target and successor")
            if self.release.predecessor_release_id != self.target_release_id:
                raise ValueError("successor predecessor must equal target")
            if self.evidence_sha256 != self.release.promotion_report_sha256:
                raise ValueError("SUPERSEDED evidence must equal successor promotion receipt SHA")
        elif self.release is not None or self.target_release_id is None:
            raise ValueError("REVOKED requires target and no successor")

    def canonical_payload(self) -> dict[str, Any]:
        return {
            "schema": _EVENT_SCHEMA,
            "sequence": self.sequence,
            "event_type": self.event_type.value,
            "previous_event_sha256": self.previous_event_sha256,
            "target_release_id": self.target_release_id,
            "release": self.release.to_payload() if self.release else None,
            "reason": self.reason,
            "evidence_sha256": self.evidence_sha256,
        }

    @property
    def sha256(self) -> str:
        return _sha(self.canonical_payload())

    def to_envelope(self) -> dict[str, Any]:
        return {"payload": self.canonical_payload(), "sha256": self.sha256}


@dataclass(frozen=True, slots=True)
class PolicyRegistryRecord:
    release: PolicyRelease
    status: PolicyReleaseStatus
    successor_release_id: str | None
    terminal_event_sequence: int | None

    def to_payload(self) -> dict[str, Any]:
        return {
            "release": self.release.to_payload(),
            "status": self.status.value,
            "successor_release_id": self.successor_release_id,
            "terminal_event_sequence": self.terminal_event_sequence,
        }


def _state(events: Sequence[PolicyRegistryEvent]) -> tuple[tuple[PolicyRegistryRecord, ...], str | None]:
    releases: dict[str, PolicyRelease] = {}
    statuses: dict[str, PolicyReleaseStatus] = {}
    successors: dict[str, str | None] = {}
    terminal: dict[str, int | None] = {}
    current: str | None = None
    for i, event in enumerate(events, start=1):
        if event.sequence != i:
            raise ValueError("event sequences must be contiguous")
        previous = _ZERO_SHA256 if i == 1 else events[i - 2].sha256
        if not hmac.compare_digest(event.previous_event_sha256, previous):
            raise ValueError("registry event hash chain is broken")
        if event.event_type is PolicyRegistryEventType.RELEASED:
            if i != 1 or releases:
                raise ValueError("RELEASED is only valid as first event")
            release = event.release
            assert release is not None
            if release.predecessor_release_id is not None:
                raise ValueError("initial release cannot have predecessor")
            releases[release.policy_release_id] = release
            statuses[release.policy_release_id] = PolicyReleaseStatus.ACTIVE
            successors[release.policy_release_id] = None
            terminal[release.policy_release_id] = None
            current = release.policy_release_id
            continue
        if current is None:
            raise ValueError("revocation is terminal for this lineage")
        if event.target_release_id != current or statuses[current] is not PolicyReleaseStatus.ACTIVE:
            raise ValueError("event must target current ACTIVE release")
        if event.event_type is PolicyRegistryEventType.SUPERSEDED:
            release = event.release
            assert release is not None
            if release.policy_release_id in releases:
                raise ValueError("duplicate policy_release_id")
            statuses[current] = PolicyReleaseStatus.SUPERSEDED
            successors[current] = release.policy_release_id
            terminal[current] = event.sequence
            releases[release.policy_release_id] = release
            statuses[release.policy_release_id] = PolicyReleaseStatus.ACTIVE
            successors[release.policy_release_id] = None
            terminal[release.policy_release_id] = None
            current = release.policy_release_id
        else:
            statuses[current] = PolicyReleaseStatus.REVOKED
            terminal[current] = event.sequence
            current = None
    records = tuple(
        PolicyRegistryRecord(releases[rid], statuses[rid], successors[rid], terminal[rid])
        for rid in releases
    )
    active = [r for r in records if r.status is PolicyReleaseStatus.ACTIVE]
    if len(active) > 1 or (current is None and active) or (current is not None and (len(active) != 1 or active[0].release.policy_release_id != current)):
        raise ValueError("registry ACTIVE state is inconsistent")
    return records, current


@dataclass(frozen=True, slots=True)
class PolicyRegistry:
    events: tuple[PolicyRegistryEvent, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "events", tuple(self.events))
        if not self.events:
            raise ValueError("registry requires at least one event")
        _state(self.events)

    @classmethod
    def create(cls, promotion: PolicyPromotionReport | Mapping[str, Any], *, reason: str = "initial promoted policy release") -> "PolicyRegistry":
        release = PolicyRelease.from_promotion(promotion)
        return cls((PolicyRegistryEvent(1, PolicyRegistryEventType.RELEASED, _ZERO_SHA256, None, release, _text(reason, "reason"), release.promotion_report_sha256),))

    @property
    def records(self) -> tuple[PolicyRegistryRecord, ...]:
        return _state(self.events)[0]

    @property
    def current_release_id(self) -> str | None:
        return _state(self.events)[1]

    @property
    def current_release(self) -> PolicyRelease | None:
        current = self.current_release_id
        return next((r.release for r in self.records if r.release.policy_release_id == current), None)

    def supersede(self, promotion: PolicyPromotionReport | Mapping[str, Any], *, reason: str) -> "PolicyRegistry":
        current = self.current_release
        if current is None:
            raise ValueError("revoked lineage cannot be superseded")
        release = PolicyRelease.from_promotion(promotion, predecessor_release_id=current.policy_release_id)
        if any(r.release.policy_release_id == release.policy_release_id for r in self.records):
            raise ValueError("promotion receipt already exists in registry lineage")
        event = PolicyRegistryEvent(
            len(self.events) + 1,
            PolicyRegistryEventType.SUPERSEDED,
            self.events[-1].sha256,
            current.policy_release_id,
            release,
            _text(reason, "reason"),
            release.promotion_report_sha256,
        )
        return PolicyRegistry(self.events + (event,))

    def revoke(self, *, reason: str, evidence_sha256: str) -> "PolicyRegistry":
        current = self.current_release
        if current is None:
            raise ValueError("registry lineage is already terminal")
        evidence_sha256 = _sha_ok(evidence_sha256, "evidence_sha256")
        event = PolicyRegistryEvent(
            len(self.events) + 1,
            PolicyRegistryEventType.REVOKED,
            self.events[-1].sha256,
            current.policy_release_id,
            None,
            _text(reason, "reason"),
            evidence_sha256,
        )
        return PolicyRegistry(self.events + (event,))

    def canonical_payload(self) -> dict[str, Any]:
        records, current = _state(self.events)
        return {
            "schema": _REGISTRY_SCHEMA,
            "events": [e.to_envelope() for e in self.events],
            "records": [r.to_payload() for r in records],
            "current_release_id": current,
            "append_only_hash_chain": True,
            "single_active_release": True,
            "revocation_is_terminal_for_lineage": True,
            "paper_policy_only": True,
        }

    @property
    def sha256(self) -> str:
        return _sha(self.canonical_payload())

    def to_envelope(self) -> dict[str, Any]:
        return {"payload": self.canonical_payload(), "sha256": self.sha256}

    @classmethod
    def from_envelope(cls, envelope: Mapping[str, Any]) -> "PolicyRegistry":
        verify_policy_registry_envelope(envelope)
        return cls(tuple(_event_from_envelope(item) for item in envelope["payload"]["events"]))


def _release_from_payload(payload: Any) -> PolicyRelease:
    keys = {"policy_release_id", "promotion_report_sha256", "policy_context_sha256", "candidate", "predecessor_release_id"}
    if not isinstance(payload, Mapping) or set(payload) != keys:
        raise ValueError("release payload is not canonical")
    candidate = payload["candidate"]
    if not isinstance(candidate, Mapping) or set(candidate) != {"execute_net_edge_bps", "volatile_return_bps"}:
        raise ValueError("release candidate payload is invalid")
    return PolicyRelease(payload["policy_release_id"], payload["promotion_report_sha256"], payload["policy_context_sha256"], JointPolicyCandidate(**dict(candidate)), payload["predecessor_release_id"])


def _event_from_envelope(envelope: Any) -> PolicyRegistryEvent:
    if not isinstance(envelope, Mapping) or set(envelope) != {"payload", "sha256"}:
        raise ValueError("event envelope is not canonical")
    payload = envelope["payload"]
    digest = _sha_ok(envelope["sha256"], "event_sha256")
    keys = {"schema", "sequence", "event_type", "previous_event_sha256", "target_release_id", "release", "reason", "evidence_sha256"}
    if not isinstance(payload, Mapping) or set(payload) != keys or payload.get("schema") != _EVENT_SCHEMA:
        raise ValueError("event payload is not canonical")
    try:
        event_type = PolicyRegistryEventType(payload["event_type"])
    except ValueError as exc:
        raise ValueError("event type is invalid") from exc
    event = PolicyRegistryEvent(
        payload["sequence"], event_type, payload["previous_event_sha256"], payload["target_release_id"],
        None if payload["release"] is None else _release_from_payload(payload["release"]), payload["reason"], payload["evidence_sha256"]
    )
    if not hmac.compare_digest(event.sha256, digest):
        raise ValueError("event SHA-256 does not match payload")
    return event


def verify_policy_registry_envelope(envelope: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(envelope, Mapping) or set(envelope) != {"payload", "sha256"}:
        raise ValueError("registry envelope is not canonical")
    payload = envelope["payload"]
    digest = _sha_ok(envelope["sha256"], "registry_sha256")
    keys = {"schema", "events", "records", "current_release_id", "append_only_hash_chain", "single_active_release", "revocation_is_terminal_for_lineage", "paper_policy_only"}
    if not isinstance(payload, dict) or set(payload) != keys or payload.get("schema") != _REGISTRY_SCHEMA:
        raise ValueError("registry payload is not canonical")
    for flag in ("append_only_hash_chain", "single_active_release", "revocation_is_terminal_for_lineage", "paper_policy_only"):
        if payload.get(flag) is not True:
            raise ValueError(f"registry invariant flag is invalid: {flag}")
    events = payload.get("events")
    if not isinstance(events, list) or not events:
        raise ValueError("registry events must be non-empty list")
    rebuilt = PolicyRegistry(tuple(_event_from_envelope(item) for item in events)).canonical_payload()
    if rebuilt != payload:
        raise ValueError("registry snapshot does not match event history")
    if not hmac.compare_digest(_sha(payload), digest):
        raise ValueError("registry SHA-256 does not match payload")
    _json(payload)
    return dict(payload)


def verify_policy_registry_promotion_bindings(registry: PolicyRegistry, promotions: Sequence[PolicyPromotionReport | Mapping[str, Any]]) -> bool:
    by_sha: dict[str, PolicyPromotionReport | Mapping[str, Any]] = {}
    for promotion in promotions:
        envelope = _envelope(promotion)
        payload = verify_policy_promotion_report_envelope(envelope)
        digest = _sha_ok(envelope.get("sha256"), "promotion_report_sha256")
        if digest in by_sha:
            raise ValueError("duplicate promotion receipt SHA supplied")
        if payload.get("decision", {}).get("status") != PolicyPromotionStatus.PROMOTED.value:
            raise ValueError("binding input contains non-promoted receipt")
        by_sha[digest] = promotion
    for record in registry.records:
        release = record.release
        promotion = by_sha.get(release.promotion_report_sha256)
        if promotion is None:
            raise ValueError("registry release is missing bound promotion receipt")
        rebuilt = PolicyRelease.from_promotion(promotion, predecessor_release_id=release.predecessor_release_id)
        if rebuilt != release:
            raise ValueError("registry release does not reproduce from promotion receipt")
    return True
