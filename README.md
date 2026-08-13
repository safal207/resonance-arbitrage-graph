# RESONANCE Arbitrage Graph

A paper-only causal verification engine for crypto-arbitrage opportunities.

The project does **not** place live orders, sign transactions, hold exchange keys, or transfer funds. Its job is to decide whether a visible market discrepancy still looks executable after modeling costs, liquidity, freshness, latency, and settlement risk — and to emit deterministic evidence for that decision.

## Causal spine

```text
market state
  -> discrepancy
  -> candidate route
  -> execution constraints
  -> state transitions
  -> settlement
  -> paper PnL
  -> evidence
```

A price difference is not treated as an opportunity by itself. The core invariant is:

```text
final simulated capital > initial capital
AND route returns to its starting asset/venue state
AND quotes are fresh
AND capacity is sufficient
AND route latency is within policy
AND modeled execution/settlement confidence is acceptable
```

## v0.1 vertical slice

- `Node` and `Edge` market graph model
- Edge costs: fee, slippage, gas
- Execution constraints: capacity, quote age, latency
- Risk inputs: failure probability, settlement probability, confidence
- DFS cycle discovery up to a configurable hop limit
- Causal route verifier
- Verdicts: `EXECUTE_SIM`, `OBSERVE`, `REJECT`
- Risk-adjusted screening score
- Deterministic paper executor
- Replay/idempotency guard using `operation_id`
- ProofPath-style deterministic evidence receipt with SHA-256
- Adversarial acceptance tests

## Quick example

```python
from resonance_arbitrage_graph import Edge, MarketGraph, Node, evaluate_route

usdt = Node("CEX", "USDT")
btc = Node("CEX", "BTC")
eth = Node("CEX", "ETH")

route = [
    Edge(usdt, btc, rate=1 / 80_000, fee_bps=5, slippage_bps=5),
    Edge(btc, eth, rate=20.0, fee_bps=5, slippage_bps=5),
    Edge(eth, usdt, rate=4_050, fee_bps=5, slippage_bps=5),
]

graph = MarketGraph(route)
cycle = graph.find_cycles(usdt, max_hops=3)[0]
result = evaluate_route(cycle, 10_000)

print(result.verdict.value)
print(result.net_edge)
```

## Why causal verification matters

A normal spread scanner can observe:

```text
buy ETH: 4,000
sell ETH: 4,030
gross spread: +0.75%
```

But after fees and slippage the route can be net-negative. RESONANCE keeps the gross signal and the executable state transition separate, so a positive spread can correctly produce `REJECT`.

## Evidence

Each evaluated route can produce a canonical JSON receipt containing:

- logical operation ID
- route edges and execution assumptions
- expected gross/net/risk-adjusted edge
- verdict and rejection reasons
- invariants
- optional observed paper-execution outcome
- SHA-256 of the canonical payload

This gives later CML-style calibration a stable record of what the system believed before execution and what happened in simulation.

## Tests

```bash
python -m pip install -e ".[test]"
pytest
```

Current acceptance coverage includes:

1. profitable cycle discovery
2. positive gross spread becoming negative after costs
3. stale quote rejection
4. insufficient capacity rejection
5. route-latency rejection
6. extra-slippage prediction error
7. replay protection
8. deterministic evidence hashing

## Safety boundary

v0.1 intentionally has no connector for exchange private APIs and no live execution path. Public market-data adapters can be added later, while execution remains paper-only until the verification model is calibrated and separately reviewed.

## Next

- public market-data adapters (CEX first, then DEX)
- quote snapshots with explicit timestamps/source identity
- richer partial-fill and price-impact model
- expected-vs-observed history and Opportunity Truth Rate
- cross-venue and cross-chain route modeling

Tracked in Issue #1: **MVP: causal paper-arbitrage verification engine**.
