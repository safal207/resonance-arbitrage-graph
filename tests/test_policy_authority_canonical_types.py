from copy import deepcopy
import hashlib
import json

import pytest

from resonance_arbitrage_graph.policy_authority import (
    PolicyAuthorityAction,
    PolicyAuthorityLedger,
    authorize_registry_event,
    make_policy_authority_registry_receipt,
)
from resonance_arbitrage_graph.policy_authority_verification import (
    verify_policy_authority_registry_receipt_envelope,
)
from resonance_arbitrage_graph.policy_registry import PolicyRegistry
from test_policy_registry import _binding


def _canonical_sha(payload: dict) -> str:
    raw = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def test_boolean_event_sequence_is_rejected_even_with_recomputed_sha():
    registry = PolicyRegistry.create(_binding().promotion_report)
    context = registry.records[0].release.policy_context_sha256
    ledger = PolicyAuthorityLedger.bootstrap(
        authority_id="governance/root",
        authority_basis="repository governance charter",
        policy_context_sha256=context,
        actions=(PolicyAuthorityAction.RELEASE,),
        evidence_sha256="a" * 64,
    )
    authorization = authorize_registry_event(
        ledger,
        registry,
        grant_id=ledger.root_grant_id,
        registry_event_sequence=1,
        evidence_sha256="b" * 64,
    )
    receipt = make_policy_authority_registry_receipt(registry, (authorization,))
    envelope = deepcopy(receipt.to_envelope())
    envelope["payload"]["event_sequences"] = [True]
    envelope["sha256"] = _canonical_sha(envelope["payload"])
    with pytest.raises(ValueError, match="integers"):
        verify_policy_authority_registry_receipt_envelope(envelope)
