from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from .policy_authority import (
    PolicyAuthorityRegistryReceipt,
    PolicyAuthorizationBinding,
    verify_policy_authority_registry_full_binding as _verify_full_binding,
    verify_policy_authority_registry_receipt_envelope as _verify_receipt_envelope,
)
from .policy_registry import PolicyRegistry


def _validate_event_sequences(values: Any) -> None:
    if not isinstance(values, (list, tuple)) or not values:
        raise ValueError("authorized registry event_sequences must be non-empty")
    for value in values:
        if isinstance(value, bool) or not isinstance(value, int) or value < 1:
            raise ValueError("authorized registry event_sequences must contain integers >= 1")


def verify_policy_authority_registry_receipt_envelope(
    envelope: Mapping[str, Any],
) -> dict[str, Any]:
    if not isinstance(envelope, Mapping):
        raise ValueError("authorized registry envelope must be a mapping")
    payload = envelope.get("payload")
    if not isinstance(payload, Mapping):
        raise ValueError("authorized registry payload must be a mapping")
    _validate_event_sequences(payload.get("event_sequences"))
    return _verify_receipt_envelope(envelope)


def verify_policy_authority_registry_full_binding(
    receipt: PolicyAuthorityRegistryReceipt | Mapping[str, Any],
    registry: PolicyRegistry | Mapping[str, Any],
    bindings: Sequence[PolicyAuthorizationBinding],
) -> bool:
    if isinstance(receipt, PolicyAuthorityRegistryReceipt):
        _validate_event_sequences(receipt.event_sequences)
    else:
        verify_policy_authority_registry_receipt_envelope(receipt)
    return _verify_full_binding(receipt, registry, bindings)
