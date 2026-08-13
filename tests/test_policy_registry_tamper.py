from copy import deepcopy
import hashlib
import json
import pytest
from resonance_arbitrage_graph.policy_registry import PolicyRegistry, verify_policy_registry_envelope
from test_policy_registry import _alternate, _binding


def _sha(payload):
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode()).hexdigest()


def test_snapshot_tamper_fails_closed():
    registry = PolicyRegistry.create(_binding().promotion_report)
    envelope = deepcopy(registry.to_envelope())
    envelope["payload"]["records"][0]["status"] = "REVOKED"
    envelope["sha256"] = _sha(envelope["payload"])
    with pytest.raises(ValueError, match="snapshot does not match"):
        verify_policy_registry_envelope(envelope)


def test_hash_chain_tamper_fails_closed():
    registry = PolicyRegistry.create(_binding().promotion_report).supersede(_alternate().promotion_report, reason="new")
    envelope = deepcopy(registry.to_envelope())
    event = envelope["payload"]["events"][1]
    event["payload"]["previous_event_sha256"] = "f" * 64
    event["sha256"] = _sha(event["payload"])
    envelope["sha256"] = _sha(envelope["payload"])
    with pytest.raises(ValueError, match="hash chain"):
        verify_policy_registry_envelope(envelope)
