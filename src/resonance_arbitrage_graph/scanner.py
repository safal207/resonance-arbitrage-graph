from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Mapping, Sequence

from .engine import Policy, evaluate_route
from .graph import MarketGraph
from .model import Edge, Node, RouteResult
from .quotes import CostAssumption, QuoteSnapshot, quote_to_trade_edges


@dataclass(frozen=True, slots=True)
class ScannedOpportunity:
    route: tuple[Edge, ...]
    result: RouteResult


@dataclass(frozen=True, slots=True)
class CrossVenueObservation:
    base_asset: str
    quote_asset: str
    buy_venue: str
    sell_venue: str
    buy_ask: float
    sell_bid: float
    gross_edge: float
    classification: str = "OBSERVE_ONLY_REBALANCE_UNMODELED"


def build_graph_from_quotes(
    quotes: Sequence[QuoteSnapshot],
    *,
    costs_by_venue: Mapping[str, CostAssumption],
    now_ms: int,
) -> MarketGraph:
    edges: list[Edge] = []
    for quote in quotes:
        try:
            costs = costs_by_venue[quote.venue]
        except KeyError as exc:
            raise ValueError(f"missing explicit cost assumptions for venue: {quote.venue}") from exc
        edges.extend(quote_to_trade_edges(quote, costs, now_ms=now_ms))
    return MarketGraph(edges)


def scan_cycles(
    quotes: Sequence[QuoteSnapshot],
    *,
    start: Node,
    amount: float,
    costs_by_venue: Mapping[str, CostAssumption],
    now_ms: int,
    max_hops: int = 3,
    policy: Policy | None = None,
) -> list[ScannedOpportunity]:
    graph = build_graph_from_quotes(quotes, costs_by_venue=costs_by_venue, now_ms=now_ms)
    opportunities = [
        ScannedOpportunity(route=route, result=evaluate_route(route, amount, policy=policy))
        for route in graph.find_cycles(start, max_hops=max_hops)
    ]
    return sorted(opportunities, key=lambda item: item.result.net_edge, reverse=True)


def observe_cross_venue_spreads(quotes: Sequence[QuoteSnapshot]) -> list[CrossVenueObservation]:
    """Surface raw cross-venue price gaps without claiming executable arbitrage.

    Rebalance/settlement edges are intentionally absent in v0.2, so these observations
    can never become EXECUTE_SIM from this function.
    """

    observations: list[CrossVenueObservation] = []
    for buy in quotes:
        for sell in quotes:
            if buy.venue == sell.venue:
                continue
            if (buy.base_asset, buy.quote_asset) != (sell.base_asset, sell.quote_asset):
                continue
            gross_edge = sell.bid_price / buy.ask_price - 1.0
            if gross_edge <= 0:
                continue
            observations.append(
                CrossVenueObservation(
                    base_asset=buy.base_asset,
                    quote_asset=buy.quote_asset,
                    buy_venue=buy.venue,
                    sell_venue=sell.venue,
                    buy_ask=buy.ask_price,
                    sell_bid=sell.bid_price,
                    gross_edge=gross_edge,
                )
            )
    return sorted(observations, key=lambda item: item.gross_edge, reverse=True)
