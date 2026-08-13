from dataclasses import replace
import json

import pytest

from resonance_arbitrage_graph import (
    Edge,
    Node,
    PaperExecutor,
    evaluate_route,
    make_evidence_receipt,
)


def simple_profitable_route():
    a = Node("CEX", "USDT")
    b = Node("CEX", "USDC")
    return [
        Edge(a, b, rate=1.01),
        Edge(b, a, rate=1.0),
    ]


def test_default_unlimited_capacity_serializes_as_strict_json():
    route = simple_profitable_route()
    result = evaluate_route(route, 1_000)
    receipt = make_evidence_receipt("strict-json", route, result)

    encoded = receipt.canonical_json()
    assert "Infinity" not in encoded
    json.loads(encoded, parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))


def test_observed_evidence_rejects_mismatched_operation_id():
    route = simple_profitable_route()
    executor = PaperExecutor()
    execution = executor.execute("arb-001", route, 1_000)

    with pytest.raises(ValueError, match="operation_id"):
        make_evidence_receipt(
            "arb-002",
            route,
            execution.expected,
            execution=execution,
        )


def test_observed_evidence_rejects_mismatched_expected_result():
    route = simple_profitable_route()
    executor = PaperExecutor()
    execution = executor.execute("arb-001", route, 1_000)
    tampered_result = replace(
        execution.expected,
        final_amount=execution.expected.final_amount + 1.0,
    )

    with pytest.raises(ValueError, match="expected result"):
        make_evidence_receipt(
            "arb-001",
            route,
            tampered_result,
            execution=execution,
        )
