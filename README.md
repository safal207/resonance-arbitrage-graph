# RESONANCE Verify

**Pre-trade verification for autonomous financial agents.**

> Send a proposed market opportunity. RESONANCE Verify checks whether it still looks executable after fees, slippage, liquidity, quote freshness, latency, market regime and historical outcome evidence — then returns a deterministic paper verdict and a reproducible evidence trail.

[![CI](https://github.com/safal207/resonance-arbitrage-graph/actions/workflows/ci.yml/badge.svg)](https://github.com/safal207/resonance-arbitrage-graph/actions/workflows/ci.yml)

## Product status

**Research core: implemented. Product proof: collecting.**

The repository contains a working public-market, paper-only verification engine, an append-only real-market corpus, leakage-safe replay and walk-forward evaluation, and an Opportunity Truth Benchmark report. It does **not** yet publish a performance or profitability claim. Any headline benchmark stays marked `NOT_READY` until the bound real-market corpus passes explicit quantity, diversity and truth-event gates.

No private exchange API, wallet key, signing, order placement, transfer, bridge or live-capital path exists in this project.

## The problem

A visible spread is not the same thing as an executable opportunity.

```text
visible discrepancy
  - fees
  - slippage
  - insufficient depth
  - stale quotes
  - latency
  - regime shift
  - settlement uncertainty
  = sometimes no opportunity at all
```

Trading agents are good at proposing actions. Before an action is trusted, someone still has to answer:

1. Does the route return capital to the intended state?
2. Are the exact quotes fresh and the capacity sufficient?
3. Does the edge survive modeled costs and latency?
4. Is the current market regime allowed by policy?
5. How often did comparable signals survive in later paper observations?
6. Can the decision and its evidence be independently replayed?

RESONANCE Verify is the verification layer between **signal** and **execution**.

```text
signal / agent proposal
        ↓
┌──────────────────┐
│ RESONANCE VERIFY │
└──────────────────┘
        ↓
EXECUTE_SIM / OBSERVE / REJECT
        ↓
deterministic evidence + later outcome
```

## Product contract

### Input today

The current implementation accepts Python objects and local/public-data CLI flows built from:

- normalized public best-bid/best-ask snapshots;
- an exact route and starting venue/asset state;
- starting capital;
- explicit fee and slippage assumptions;
- freshness, latency, regime and execution policies;
- optional historical replay/outcome evidence.

A REST/SDK adapter is a product-integration layer, not yet an advertised hosted service.

### Output

Every proposed route receives one of three paper verdicts:

- `EXECUTE_SIM` — the route passes the deterministic paper policy;
- `OBSERVE` — the signal is interesting but not eligible for simulated execution;
- `REJECT` — one or more hard constraints fail.

Illustrative response shape — **not a measured benchmark result**:

```json
{
  "verdict": "OBSERVE",
  "base_verdict": "EXECUTE_SIM",
  "market_regime": "VOLATILE",
  "regime_action": "OBSERVE_ONLY",
  "expected_edge_bps": 18.4,
  "checks": {
    "fresh_quotes": true,
    "capacity_sufficient": true,
    "route_continuous": true
  },
  "reasons": [
    "derived market regime requires a monotonic downgrade"
  ],
  "evidence_sha256": "…"
}
```

The exact wire objects are content-addressed and validated in the Python core; the example above is deliberately simplified for product orientation.

## Opportunity Truth Benchmark

The product claim is not “we find the largest spread.” It is:

> **RESONANCE Verify separates opportunities that merely look profitable from opportunities that survive the full paper-verification chain.**

The new benchmark consumes a bound `RealMarketReplayCorpus` or `ReplayBundle` and emits canonical JSON + SHA-256 plus a human-readable report.

Core metrics:

```text
Opportunity Truth Rate = TP / (TP + FP)
False Opportunity Rate = FP / (TP + FP)
Route Survival Rate     = (TP + FP) / (TP + FP + EXPIRED)
Truth Coverage          = (TP + FP) / EXECUTE_SIM
Edge Decay              = expected edge - observed edge
```

Important semantics:

- `REJECT` is not counted as a false positive because the system never claimed it was executable;
- `OBSERVE` and unresolved outcomes do not enter the OTR denominator;
- retries collapse to one logical opportunity;
- paper PnL is grouped by exact starting `venue:asset` state and is never blended across incompatible units;
- a replay fixture can be measured, but only a quality-gated append-only real-market corpus can become `INTERNAL_EVIDENCE_READY`;
- even `INTERNAL_EVIDENCE_READY` is not a live-fill or profitability claim.

Build a benchmark from a local corpus:

```bash
resonance-opportunity-truth-benchmark build corpus.json \
  --format json \
  --output opportunity-truth-benchmark.json
```

Render a product-readable Markdown report:

```bash
resonance-opportunity-truth-benchmark render \
  opportunity-truth-benchmark.json \
  --output opportunity-truth-benchmark.md
```

Reproduce the report from its bound source:

```bash
resonance-opportunity-truth-benchmark verify \
  opportunity-truth-benchmark.json \
  corpus.json
```

A successful full check prints:

```text
FULL_OK
```

## Collect real public-market evidence

Install locally:

```bash
python -m pip install -e ".[test]"
```

The one-shot corpus runner performs:

```text
public decision capture
→ persist before waiting
→ configured paper horizon
→ fresh public outcome capture
→ append-only outcome record
→ replay-bundle export
→ quantity + quality readiness checks
→ optional shadow benchmark
```

Example shape:

```bash
resonance-corpus-runner \
  --corpus corpus.json \
  --venue binance \
  --pair BTCUSDT:BTC:USDT \
  --pair ETHBTC:ETH:BTC \
  --pair ETHUSDT:ETH:USDT \
  --start-asset USDT \
  --amount 1000 \
  --fee-bps 10 \
  --slippage-bps 5 \
  --outcome-horizon-ms 60000
```

Run `resonance-corpus-runner --help` for the exact installed options. Public feeds currently include Binance Spot and Kraken Spot adapters.

## Why the evidence is different

The engine does not trust stored labels when it can recompute them.

```text
public quotes
→ route reconstruction
→ cost / capacity / freshness checks
→ rolling market state
→ regime derivation
→ monotonic execution gate
→ paper verdict
→ later public outcome
→ truth classification
→ replay / benchmark
```

Evidence and governance layers include:

- deterministic route and quote provenance;
- append-only outcome identity across retries;
- hash-chained real-market corpus records;
- anti-lookahead replay and chronological splits;
- holdout and walk-forward evaluation;
- corpus quantity and diversity gates;
- policy promotion, lineage, revocation and scoped authority receipts;
- predictive models restricted to shadow ranking/downgrade behavior.

No model can turn deterministic `OBSERVE` or `REJECT` into `EXECUTE_SIM`.

## Who this is for

The first design-partner profile is deliberately narrow:

- teams building autonomous or agentic trading systems;
- quant/trading infrastructure teams that need an independent pre-trade verifier;
- strategy QA and risk teams that need reproducible replay rather than screenshots of historical spreads.

Potential integrations:

```text
trading agent → RESONANCE Verify → existing execution stack
signal service → RESONANCE Verify → risk review queue
strategy candidate → replay corpus → Opportunity Truth Benchmark
```

## Current product roadmap

### Now — Product 0.1

- product-first interface and examples;
- repeated real-market corpus collection;
- Opportunity Truth Benchmark;
- design-partner discovery;
- one narrow integration contract before adding more research layers.

### Next — chosen by evidence, not version numbers

- Verify API/SDK if partners need a pre-execution integration;
- predictive ranking only after the real corpus is claim-ready;
- wallet follower-edge verification only after the arbitrage wedge is validated;
- cryptographic identity/signature attestation only when an enterprise workflow requires it.

## Safety boundary

RESONANCE Verify is **paper-only research and verification infrastructure**.

It does not:

- give personalized investment advice;
- guarantee profit;
- place orders;
- connect private exchange accounts;
- hold or sign with wallet keys;
- move assets;
- initiate transfers or bridges;
- allocate live capital;
- automatically activate a learned model or promoted policy.

Public top-of-book paper outcomes are not the same as executable fills. Benchmark reports state that limitation explicitly.

## Technical map

```text
v0.1–v0.6   verification, public quotes, regimes, rolling state
v0.7–v0.12  replay, holdout, causal calibration, walk-forward, decomposition
v0.13–v0.15 promotion, lineage, revocation, authority
v0.16       leakage-safe predictive contracts and shadow CatBoost baseline
v0.16.2     append-only real-market replay corpus
v0.16.3     one-shot corpus runner and quantity readiness
v0.16.4     corpus diversity / evidence-quality gate
Product 0.1 product surface + Opportunity Truth Benchmark
```

Design documents live in [`docs/`](docs/), including:

- [`docs/market-data-contracts.md`](docs/market-data-contracts.md)
- [`docs/v0.16-design.md`](docs/v0.16-design.md)
- [`docs/v0.16.2-design.md`](docs/v0.16.2-design.md)
- [`docs/v0.16.3-design.md`](docs/v0.16.3-design.md)
- [`docs/v0.16.4-design.md`](docs/v0.16.4-design.md)
- [`docs/product-brief.md`](docs/product-brief.md)
- [`docs/opportunity-truth-benchmark.md`](docs/opportunity-truth-benchmark.md)

## License

Apache-2.0.
