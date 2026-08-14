from dataclasses import replace

import pytest

from resonance_arbitrage_graph.policy_authority import (
    PolicyAuthorityAction,
    PolicyAuthorityLedger,
    authorize_registry_event,
    make_policy_authority_registry_receipt,
)
from resonance_arbitrage_graph.policy_registry import PolicyRegistry
from test_policy_registry import _alternate, _binding


def test_registry_receipt_missing_sequence_raises_value_error():
    first, second = _binding(), _alternate()
    initial = PolicyRegistry.create(first.promotion_report)
    registry = initial.supersede(second.promotion_report, reason="new calibrated policy")
    context = registry.records[0].release.policy_context_sha256
    ledger = PolicyAuthorityLedger.bootstrap(
        authority_id="governance/root",
        authority_basis="repository governance charter",
        policy_context_sha256=context,
        actions=(
            PolicyAuthorityAction.RELEASE,
            PolicyAuthorityAction.SUPERSEDE,
        ),
        evidence_sha256="a" * 64,
    )
    auth1 = authorize_registry_event(
        ledger,
        registry,
        grant_id=ledger.root_grant_id,
        registry_event_sequence=1,
        evidence_sha256="b" * 64,
    )
    auth2 = authorize_registry_event(
        ledger,
        registry,
        grant_id=ledger.root_grant_id,
        registry_event_sequence=2,
        evidence_sha256="c" * 64,
    )
    malformed = replace(auth2, registry_event_sequence=3)

    with pytest.raises(ValueError, match="cover each registry event sequence"):
        make_policy_authority_registry_receipt(registry, (auth1, malformed))
