import pytest

from resonance_arbitrage_graph import Edge, Node


def test_negative_execution_cost_is_rejected():
    a = Node("CEX", "USDT")
    b = Node("CEX", "ETH")

    with pytest.raises(ValueError):
        Edge(a, b, rate=1.0, fee_bps=-1)
