import json

from resonance_arbitrage_graph import Edge, Node, evaluate_route, make_evidence_receipt


def test_default_unlimited_capacity_serializes_as_strict_json():
    a = Node("CEX", "USDT")
    b = Node("CEX", "USDC")
    route = [
        Edge(a, b, rate=1.01),
        Edge(b, a, rate=1.0),
    ]
    result = evaluate_route(route, 1_000)
    receipt = make_evidence_receipt("strict-json", route, result)

    encoded = receipt.canonical_json()
    assert "Infinity" not in encoded
    json.loads(encoded, parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))
