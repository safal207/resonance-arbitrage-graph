# RESONANCE Verify

**Pre-trade verification for autonomous financial agents.**

A visible spread is not the same thing as an executable opportunity.

RESONANCE Verify takes a candidate market route and asks a stricter question:

> **After fees, slippage, liquidity, freshness, latency, market regime and historical reliability — is this opportunity still real enough to act on?**

It returns a paper-only verdict plus deterministic evidence that can be replayed and independently checked.

```text
agent / scanner proposes an opportunity
                ↓
        RESONANCE VERIFY
                ↓
   EXECUTE_SIM / OBSERVE / REJECT
                ↓
      evidence + later outcome
                ↓
        truth / reliability
```

The repository is still named `resonance-arbitrage-graph` because arbitrage is the first verification domain. The product surface is **RESONANCE Verify**.

## The problem

Trading systems often begin with something that *looks* profitable:

```text
price discrepancy
→ estimated edge
→ trade candidate
```

But the candidate can disappear after real constraints are applied:

- fees and slippage;
- insufficient depth;
- stale quotes;
- route latency;
- market-regime changes;
- settlement assumptions;
- historical false-positive behavior.

RESONANCE Verify sits between **signal** and **execution**.

```text
SIGNAL
  ↓
┌──────────────────┐
│ RESONANCE VERIFY │
└──────────────────┘
  ↓
EXECUTION SYSTEM
```

It does not try to own the trading strategy or manufacture alpha. It verifies a proposed action against explicit, evidence-bound constraints.

## What the verifier returns

A product-facing result is conceptually this simple:

```text
VERDICT: OBSERVE

Expected raw/net edge:        +42 bps
Required execution edge:      +30 bps
Market regime:                VOLATILE
Regime action:                OBSERVE_ONLY

Freshness:                    verified from captured quote provenance
Liquidity/capacity:           checked by route verifier
Costs:                        explicit fee + slippage assumptions
Historical outcome class:     tracked after later observation

Reason:
The route remains positive on paper, but the active regime gate
prevents EXECUTE_SIM under the current volatility evidence.

Evidence SHA-256:
<deterministic receipt digest>
```

The exact internal receipt contains substantially more information. The point of the product layer is that a caller should not need to understand the whole research stack to use the verdict.

## Current interface

Today the project exposes a Python library and offline/read-only CLIs. An HTTP `POST /verify` product API is a future packaging step; it is **not claimed as shipped yet**.

Install for local development:

```bash
python -m pip install -e ".[test]"
```

Example public-data paper scan:

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
  --max-hops 3 \
  --rolling-samples 5 \
  --rolling-interval-ms 1000 \
  --rolling-horizon-ms 5000 \
  --rolling-min-coverage-ratio 0.8
```

These values are examples, not trading recommendations.

## Opportunity Truth Benchmark

The core product claim must be proven with observed outcomes, not marketing copy.

The benchmark asks:

> **Of the opportunities that RESONANCE marked `EXECUTE_SIM`, how many actually survived long enough to clear the required paper edge?**

Primary metrics:

```text
Opportunity Truth Rate = TP / (TP + FP)
False Opportunity Rate = FP / (TP + FP)
Route Survival Rate    = (TP + FP) / (TP + FP + EXPIRED)
```

Product 0.1 also reports:

- total candidate opportunities;
- `EXECUTE_SIM / OBSERVE / REJECT` counts;
- true positives, false positives, expired, rejected and indeterminate outcomes;
- expected-vs-realized edge error;
- capital-weighted realized **paper** PnL for evaluated `EXECUTE_SIM` decisions;
- regime and route segmentation;
- downgrade / rejection reason counts.

### No invented benchmark number

There is intentionally **no headline percentage in this README yet**.

Fixture or synthetic replay results are useful for tests, but they are not a product claim. Public benchmark claims must come from a captured real-market corpus.

The benchmark enforces a configurable sample-size gate. The default requires at least 30 determinate `TP + FP` outcomes before the report changes from:

```text
INSUFFICIENT_TRUTH_POPULATION
```

to:

```text
READY
```

`READY` means the minimum sample-size guardrail passed. It does **not** by itself prove profitability or statistical significance.

### Build a benchmark

From a captured real-market corpus or replay bundle:

```bash
resonance-opportunity-truth-benchmark build real-market-corpus.json \
  --output opportunity-truth-report.json \
  --markdown-output opportunity-truth-report.md
```

Verify the report by reproducing it from the same evidence:

```bash
resonance-opportunity-truth-benchmark verify \
  real-market-corpus.json \
  opportunity-truth-report.json
```

The report is canonical JSON + SHA-256 and is rebuilt from replay evidence during verification rather than trusting the outer digest alone.

## Existing real-market evidence pipeline

The repository already contains a public-market corpus path:

```text
public market snapshots
→ decision-time capture
→ hash-chained real-market corpus
→ later public outcome capture
→ replay bundle
→ deterministic benchmark
```

Relevant CLIs include:

```text
resonance-real-market-corpus
resonance-corpus-runner
resonance-replay-benchmark
resonance-opportunity-truth-benchmark
```

This means Product 0.1 is not waiting for a future data model: the benchmark can sit on top of the evidence pipeline that already exists.

## Who this is for

The first design-partner profiles are deliberately narrow.

### 1. Agentic trading builders

Systems where an agent proposes a financial action before another component executes it.

```text
agent proposes trade
→ RESONANCE Verify
→ allow paper execution / observe / reject
```

The product question is:

> **When your trading agent sees an opportunity, how do you verify it is still executable before letting it act?**

### 2. Quant / trading infrastructure teams

Teams that want an independent replay and pre-trade verification layer without handing over strategy ownership.

RESONANCE can verify the candidate while the team keeps its own alpha logic private.

### 3. Financial-agent infrastructure

Programmable-wallet, treasury, payment and autonomous-finance systems where an action should be checked against explicit invariants before execution.

Arbitrage is the first domain, not the limit of the verification model.

## Why this is more than a spread scanner

The causal model is:

```text
market state
→ discrepancy
→ candidate route
→ execution constraints
→ state transitions
→ settlement assumptions
→ paper outcome
→ evidence
→ later truth
```

A route can only reach `EXECUTE_SIM` after the deterministic verifier and the monotonic regime gate allow it. A later outcome is then recorded and used to measure whether that confidence was deserved.

The verifier cannot upgrade a failed base decision through history or prediction.

```text
REJECT < OBSERVE < EXECUTE_SIM

final_verdict <= base_verdict
```

## Trust infrastructure already underneath the product

The product-facing verdict sits on a deeper research core:

```text
public market evidence
→ deterministic route verification
→ rolling market state
→ regime gate
→ outcome memory
→ truth metrics
→ reliability ranking
→ replay
→ chronological holdout
→ causal calibration
→ untouched validation
→ walk-forward stability
→ stability decomposition
→ policy promotion
→ canonical policy lineage / revocation
→ policy authority / delegation
```

Those layers exist so the product can answer more than “the number looked good.” They provide provenance for what was observed, which policy was active, why it was allowed, how it performed later and whether the governing policy itself was valid.

## Safety boundary

RESONANCE Verify remains **paper-only**.

It does not:

- place live orders;
- sign transactions;
- store exchange or wallet private keys;
- initiate transfers or bridges;
- allocate live capital;
- provide copy-trading automation.

Public market adapters use read-only market data. Replay, calibration, governance and benchmark layers operate on local evidence artifacts.

## Product roadmap

The next product decisions are intentionally evidence-driven rather than version-number-driven.

```text
if users need better ranking
→ predictive shadow scoring

if users need an integration point
→ Verify API / SDK

if users need wallet-signal copyability
→ Wallet Intelligence

if enterprises need authenticated governance identity
→ cryptographic authority attestation

if quant teams value replay most
→ Replay / Benchmark as a service
```

The market should choose the next deep research layer.

## Technical documentation

Research and design details live under `docs/` rather than at the top of the product page.

Key documents include:

- `docs/market-data-contracts.md`
- `docs/v0.2-design.md` through the later versioned design notes
- `docs/v0.12-design.md` — stability decomposition
- `docs/v0.13-design.md` — policy promotion
- `docs/v0.14-design.md` — canonical policy lineage and revocation
- `docs/v0.15-design.md` — authority and delegation

The implementation also contains experimental predictive and real-market corpus tooling. Predictive research is advisory/shadow work and does not bypass the deterministic verification chain.

## Tests

```bash
pytest
```

Coverage spans route verification, quote provenance, retry identity, outcome truth accounting, replay determinism, anti-lookahead constraints, calibration/validation firewalls, walk-forward stability, governance receipts, tamper rejection and benchmark reproduction.

---

### Product thesis

**A financial agent should not act merely because it found a signal. It should be able to prove why the proposed action still satisfies its execution invariants.**
