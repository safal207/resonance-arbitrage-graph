from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable

from .model import Edge, Node


class MarketGraph:
    def __init__(self, edges: Iterable[Edge] = ()) -> None:
        self._adjacency: dict[Node, list[Edge]] = defaultdict(list)
        for edge in edges:
            self.add_edge(edge)

    def add_edge(self, edge: Edge) -> None:
        self._adjacency[edge.src].append(edge)

    def edges_from(self, node: Node) -> tuple[Edge, ...]:
        return tuple(self._adjacency.get(node, ()))

    def find_cycles(self, start: Node, *, max_hops: int = 3) -> list[tuple[Edge, ...]]:
        if max_hops < 2:
            return []

        cycles: list[tuple[Edge, ...]] = []

        def dfs(node: Node, path: list[Edge], visited: set[Node]) -> None:
            if len(path) >= max_hops:
                return

            for edge in self._adjacency.get(node, ()):
                next_path = [*path, edge]

                if edge.dst == start:
                    if len(next_path) >= 2:
                        cycles.append(tuple(next_path))
                    continue

                if edge.dst in visited:
                    continue

                dfs(edge.dst, next_path, visited | {edge.dst})

        dfs(start, [], {start})
        return cycles
