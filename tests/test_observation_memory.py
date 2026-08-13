import hashlib

import pytest

from resonance_arbitrage_graph.evidence import EvidenceReceipt
from resonance_arbitrage_graph.journal import JournalError, ObservationJournal
from resonance_arbitrage_graph.metrics import calculate_metrics
from resonance_arbitrage_graph.observation import (
    OutcomeClass,
    observation_from_evidence,
    verify_evidence_receipt,
)


def _receipt(
    operation_id: str,
    *,
    verdict: str = "EXECUTE_SIM",
    expected_edge: float = 0.0020,
    observed_edge: float | None = None,
) -> EvidenceReceipt:
    payload = {
        "schema": "resonance.arbitrage.evidence/v0.1",
        "paper_only": True,
        "logical_operation_id": operation_id,
        "expected": {
            "net_edge": expected_edge,
            "verdict": verdict,
        },
    }
    if observed_edge is not None:
        payload["observed"] = {"realized_net_edge": observed_edge}
    draft = EvidenceReceipt(payload=payload, sha256="0" * 64)
    digest = hashlib.sha256(draft.canonical_json().encode("utf-8")).hexdigest()
    return EvidenceReceipt(payload=payload, sha256=digest)


def _observation(
    operation_id: str,
    execution_id: str,
    attempt: int,
    *,
    observed_edge: float | None,
    verdict: str = "EXECUTE_SIM",
    required_edge_bps: float = 10.0,
    expired: bool = False,
):
    return observation_from_evidence(
        _receipt(
            operation_id,
            verdict=verdict,
            expected_edge=0.0020,
            observed_edge=observed_edge,
        ),
        execution_id=execution_id,
        attempt=attempt,
        opportunity_id="opp-1",
        route_id="USDT-BTC-ETH-USDT",
        detected_at_ms=1_000,
        observed_at_ms=1_000 + attempt * 100,
        required_edge_bps=required_edge_bps,
        expired=expired,
        market_context={"venue": "binance", "regime": "fixture"},
    )


def test_receipt_digest_is_verified():
    receipt = _receipt("op-1", observed_edge=0.0015)
    verify_evidence_receipt(receipt)

    tampered = EvidenceReceipt(
        payload={**receipt.payload, "logical_operation_id": "op-2"},
        sha256=receipt.sha256,
    )
    with pytest.raises(ValueError, match="does not match payload"):
        verify_evidence_receipt(tampered)


def test_outcome_is_derived_from_receipt():
    true_positive = _observation("op-1", "exec-1", 1, observed_edge=0.0015)
    false_positive = _observation("op-2", "exec-2", 1, observed_edge=0.0005)
    rejected = _observation("op-3", "exec-3", 1, observed_edge=None, verdict="REJECT")
    expired = _observation("op-4", "exec-4", 1, observed_edge=None, expired=True)

    assert true_positive.outcome_class is OutcomeClass.TRUE_POSITIVE
    assert false_positive.outcome_class is OutcomeClass.FALSE_POSITIVE
    assert rejected.outcome_class is OutcomeClass.REJECTED
    assert expired.outcome_class is OutcomeClass.EXPIRED
    assert true_positive.prediction_error_bps == pytest.approx(-5.0)


def test_retry_counts_once_and_terminal_blocks_replay(tmp_path):
    journal = ObservationJournal(tmp_path / "observations.jsonl")
    journal.append(_observation("op-1", "exec-1", 1, observed_edge=None))
    journal.append(_observation("op-1", "exec-2", 2, observed_edge=0.0015))

    metrics = calculate_metrics(journal.load())
    assert metrics.logical_operations == 1
    assert metrics.true_positive == 1
    assert metrics.indeterminate == 0
    assert metrics.opportunity_truth_rate == 1.0

    with pytest.raises(JournalError, match="terminal outcome"):
        journal.append(_observation("op-1", "exec-3", 3, observed_edge=0.0016))


def test_journal_rejects_duplicate_execution_and_attempt_gap(tmp_path):
    journal = ObservationJournal(tmp_path / "observations.jsonl")
    journal.append(_observation("op-1", "exec-1", 1, observed_edge=None))

    with pytest.raises(JournalError, match="duplicate execution_id"):
        journal.append(_observation("op-2", "exec-1", 1, observed_edge=None))

    with pytest.raises(JournalError, match="increment by exactly one"):
        journal.append(_observation("op-1", "exec-3", 3, observed_edge=0.0015))


def test_truth_metrics_exclude_rejected_and_indeterminate():
    observations = [
        _observation("tp", "exec-tp", 1, observed_edge=0.0015),
        _observation("fp", "exec-fp", 1, observed_edge=0.0005),
        _observation("reject", "exec-r", 1, observed_edge=None, verdict="REJECT"),
        _observation("pending", "exec-p", 1, observed_edge=None),
        _observation("expired", "exec-e", 1, observed_edge=None, expired=True),
    ]

    metrics = calculate_metrics(observations)
    assert metrics.logical_operations == 5
    assert metrics.true_positive == 1
    assert metrics.false_positive == 1
    assert metrics.rejected == 1
    assert metrics.indeterminate == 1
    assert metrics.expired == 1
    assert metrics.opportunity_truth_rate == 0.5
    assert metrics.false_opportunity_rate == 0.5
    assert metrics.route_survival_rate == pytest.approx(2 / 3)
    assert metrics.mean_prediction_error_bps == pytest.approx(-10.0)


def test_journal_row_is_canonical_and_round_trips(tmp_path):
    journal = ObservationJournal(tmp_path / "observations.jsonl")
    observation = _observation("op-1", "exec-1", 1, observed_edge=0.0015)
    journal.append(observation)

    raw = journal.path.read_text(encoding="utf-8")
    assert raw == observation.canonical_json() + "\n"
    assert journal.load() == [observation]
