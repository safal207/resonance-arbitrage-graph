# RESONANCE Arbitrage Graph

A paper-only causal verification engine for crypto-arbitrage opportunities.

The project does **not** place live orders, sign transactions, hold exchange keys, or transfer funds. Its job is to decide whether a visible market discrepancy still looks executable after modeling costs, liquidity, freshness, latency, and settlement risk — and to emit deterministic evidence and outcome memory for that decision.

## Causal spine

```text
public/fixture market state
  -> normalized quote snapshot
  -> verified pair metadata
  -> discrepancy
  -> candidate route
  -> execution constraints
  -> state transitions
  -> settlement assumptions
  -> paper PnL
  -> quote-bound evidence
  -> opportunity observation
  -> truth metrics
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

## v0.3 — Opportunity Memory & Truth Metrics

v0.3 records whether opportunities that looked executable actually survive the paper execution path.

- `OpportunityObservation` binds a logical opportunity, concrete execution attempt, expected/observed edge, truth class and evidence SHA-256.
- `observation_from_evidence(...)` recomputes the receipt digest, takes `logical_operation_id` from the receipt, and derives edge/verdict/outcome instead of trusting duplicate caller claims.
- `ObservationJournal` is an append-only deterministic JSONL journal with flush + fsync.
- Retries use a new `execution_id` under the same `logical_operation_id` and must increment `attempt` exactly once.
- Retry identity cannot drift across `opportunity_id`, `route_id` or detection time.
- Terminal outcomes block later replay attempts.
- Truth classes: `TRUE_POSITIVE`, `FALSE_POSITIVE`, `EXPIRED`, `REJECTED`, `INDETERMINATE`.
- `REJECTED` and `INDETERMINATE` are excluded from Opportunity Truth Rate rather than mislabeled as false positives.

Metrics:

```text
Opportunity Truth Rate
  = TP / (TP + FP)

False Opportunity Rate
  = FP / (TP + FP)

Route Survival Rate
  = (TP + FP) / (TP + FP + EXPIRED)

Prediction Error
  = observed_edge_bps - expected_edge_bps
```

The v0.3 file journal is intentionally **single-writer**. Multi-process locking/database storage is a future layer and must preserve the same causal identity and terminal-state invariants.

## v0.2 — public read-only market data

v0.2 connects real public quotes to the existing verifier while keeping execution strictly paper-only.

- `QuoteSnapshot` normalizes venue, pair, best bid/ask, quantities, timestamps and source identity.
- Binance Spot verifies pair metadata through public `exchangeInfo`, then consumes public `bookTicker` for best bid/ask.
- Kraken Spot consumes public `PreTrade`, which supplies top-of-book data, pair metadata and publication timestamps.
- Quote snapshots become buy/sell graph edges with top-of-book capacity.
- Fee/slippage assumptions are explicit caller inputs; the engine does not guess a user's fee tier.
- Single-venue triangular cycles can be evaluated with real public quotes.
- Cross-venue gaps are deliberately classified `OBSERVE_ONLY_REBALANCE_UNMODELED` until transfer/rebalance/settlement edges exist.
- Public quote provenance is bound into deterministic SHA-256 evidence by venue, pair, side, rate, capacity and freshness at evaluation time.

### Live paper scan

Install:

```bash
python -m pip install -e ".[test]"
```

Example Binance triangle:

```bash
resonance-live-scan \
  --venue binance \
  --pair BTCUSDT:BTC:USDT \
  --pair ETHBTC:ETH:BTC \
  --pair ETHUSDT:ETH:USDT \
  --start-asset USDT \
  --amount 1000 \
  --fee-bps 10 \
  --slippage-bps 5 \
  --max-hops 3
```

`--fee-bps` and `--slippage-bps` are **paper-model assumptions**, not claims about your actual exchange account.

Each surfaced cycle includes a logical operation ID, deterministic evidence SHA-256 and explicit edge-to-snapshot market bindings.

Kraken uses the same CLI shape; pair symbols may contain `/`, for example `BTC/USDT:BTC:USDT`.

## v0.1 — verification core

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

## Evidence

The base evidence receipt contains:

- logical operation ID
- route edges and execution assumptions
- expected gross/net/risk-adjusted edge
- verdict and rejection reasons
- invariants
- optional observed paper-execution outcome
- SHA-256 of the canonical payload

`make_market_evidence_receipt(...)` additionally binds the public quote snapshots and evaluation time used for the decision. It refuses to produce a receipt if an edge cannot be derived from exactly one supplied snapshot using the expected venue, asset direction, price, top-of-book capacity and quote age.

v0.3 does not accept the receipt digest at face value: the observation layer recomputes the SHA-256 over canonical receipt JSON before admitting it to memory.

## Why cross-venue is observe-only

Buying on venue A and selling on venue B does not return capital to the same venue state. Calling that an executable cycle without modeling inventory/rebalance would hide a real state transition.

A later version can add explicit transfer/rebalance edges with:

```text
withdraw/deposit availability
fees
latency
capacity
chain/bridge state
settlement probability
```

Until those edges exist, cross-venue gaps are observations, not `EXECUTE_SIM` routes.

## Tests

```bash
pytest
```

Coverage includes:

- verifier/replay/base evidence contracts
- normalized quote and timestamp-provenance validation
- top-of-book capacity mapping
- mocked Binance and Kraken public adapters
- live-shaped triangular quote graph
- cross-venue observe-only boundary
- route-edge ↔ quote-price/capacity/freshness provenance binding
- tampered quote and forged quote-age rejection
- evidence-digest tamper rejection before observation memory
- retry collapse without truth-metric double-counting
- duplicate execution and attempt-gap rejection
- terminal-state replay rejection
- canonical JSONL journal round-trip

## Safety boundary

The system remains paper-only. The market-data layer implements GET-only public data. There is no private API-key handling, signing, account endpoint, order endpoint, wallet interaction, or fund-transfer path.

See:

- `docs/market-data-contracts.md`
- `docs/v0.2-design.md`
- `docs/v0.3-design.md`
- Issue #5 — v0.3 Opportunity Memory & Truth Metrics
