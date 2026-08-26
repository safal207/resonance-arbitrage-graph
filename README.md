# RESONANCE Verify

**Evidence-bound pre-trade verification for autonomous financial agents.**

A visible spread is not the same thing as an executable opportunity.

RESONANCE Verify takes a proposed market route and asks a stricter question:

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

The repository remains named `resonance-arbitrage-graph` because arbitrage is the first verification domain. The product surface is **RESONANCE Verify**.

## The problem

Trading systems often begin with something that *looks* profitable:

```text
price discrepancy
→ estimated edge
→ trade candidate
```

But that candidate can disappear after real constraints are applied:

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

Freshness:                    verified from quote provenance
Liquidity/capacity:           checked by route verifier
Costs:                        explicit fee + slippage assumptions
Historical outcome class:     tracked after later observation

Reason:
The route remains positive on paper, but the active regime gate
prevents EXECUTE_SIM under the current volatility evidence.

Evidence SHA-256:
<deterministic receipt digest>
```

The exact receipt contains more provenance. The product layer exists so a caller does not have to understand the whole research stack to use the verdict.

## Current interface

The project currently exposes a Python library and offline/read-only CLIs. An HTTP `POST /verify` API is a future packaging step; it is **not claimed as shipped**.

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

## Opportunity Truth Benchmark v0.2

The product claim must be proven with observed outcomes, not marketing copy.

The benchmark asks:

> **Of the opportunities that RESONANCE marked `EXECUTE_SIM`, how many later survived and still cleared the required paper edge?**

Primary metrics:

```text
Opportunity Truth Rate = TP / (TP + FP)
False Opportunity Rate = FP / (TP + FP)
Route Survival Rate    = (TP + FP) / (TP + FP + EXPIRED)
Truth Coverage         = (TP + FP) / EXECUTE_SIM
Edge Decay             = mean(expected edge) - mean(observed edge)
```

The report also preserves:

- total candidate and `EXECUTE_SIM / OBSERVE / REJECT` counts;
- true positives, false positives, expired, rejected and indeterminate outcomes;
- expected and observed edge for determinate truth events;
- exact route and market-regime slices through the embedded v0.1 report;
- downgrade and rejection reason counts;
- paper PnL grouped by exact starting `venue:asset` state;
- corpus quantity, diversity and concentration evidence;
- exact logical-operation membership and source hashes.

### Honest outcome accounting

- `REJECT` is not a false positive because the verifier never claimed the route was executable.
- `OBSERVE` and unresolved outcomes do not enter OTR.
- Retries collapse to one logical operation.
- A high OTR with low truth coverage remains weak evidence.
- BTC, ETH, USDT, EUR or balances on different venues are never added into one fake PnL total.

For one determinate operation:

```text
expected_pnl_units = start_amount × expected_edge_bps / 10,000
observed_pnl_units = start_amount × observed_edge_bps / 10,000
```

Those units remain attached to the exact starting state, for example `binance:USDT` or `fixture:BTC`.

### No invented benchmark number

There is intentionally **no headline percentage in this README yet**.

Fixture and synthetic replays remain useful for tests, but their claim status is:

```text
UNASSESSED_REPLAY_SOURCE
```

Only an append-only public `RealMarketReplayCorpus` can become eligible for automated internal evidence review.

### Claim-readiness statuses

```text
NOT_READY
```

A real-market corpus exists, but one or more terminal-count, truth-population or corpus-quality gates fail.

```text
INTERNAL_EVIDENCE_READY
```

The configured quantity and corpus-quality checks pass. This is **internal evidence readiness only**. It is not publication approval, proof of profitability, statistical significance, a live-fill result, future-performance assurance or permission to activate a policy.

```text
UNASSESSED_REPLAY_SOURCE
```

The report came from a `ReplayBundle` without real-market corpus claim provenance.

Default internal-readiness gates include:

```text
minimum terminal operations: 100
minimum determinate truth events: 30
corpus quality required: true
```

The bound corpus-quality report checks independent decision batches, effective batch count, temporal span, route diversity, market diversity, regime diversity and concentration. A hundred correlated routes from one market moment do not earn a trustworthy product claim.

### Build, render and verify

Build JSON and Markdown from a captured corpus:

```bash
resonance-opportunity-truth-benchmark build real-market-corpus.json \
  --output opportunity-truth-v0.2.json \
  --markdown-output opportunity-truth-v0.2.md
```

Example explicit guardrails:

```bash
resonance-opportunity-truth-benchmark build real-market-corpus.json \
  --min-terminal-operations 100 \
  --min-truth-population 30 \
  --min-decision-batches 20 \
  --min-effective-decision-batches 10 \
  --min-temporal-span-ms 3600000 \
  --min-distinct-routes 3 \
  --min-effective-routes 2 \
  --min-distinct-route-markets 3 \
  --min-distinct-regimes 2 \
  --output benchmark.json
```

Verify the report by reproducing it from the same evidence:

```bash
resonance-opportunity-truth-benchmark verify \
  real-market-corpus.json \
  opportunity-truth-v0.2.json
```

A successful full check prints:

```text
FULL_OK
```

Render an existing envelope:

```bash
resonance-opportunity-truth-benchmark render \
  opportunity-truth-v0.2.json \
  --output opportunity-truth-v0.2.md
```

## Real-market evidence pipeline

The repository already contains a public-market corpus path:

```text
public market snapshots
→ decision-time capture
→ persist before waiting
→ later public outcome capture
→ append-only hash-chained corpus
→ replay bundle
→ quantity + diversity gates
→ deterministic benchmark
```

Relevant CLIs:

```text
resonance-real-market-corpus
resonance-corpus-runner
resonance-replay-benchmark
resonance-opportunity-truth-benchmark
```

## Who this is for

### 1. Agentic trading builders

Systems where an agent proposes a financial action before another component executes it.

```text
agent proposes trade
→ RESONANCE Verify
→ EXECUTE_SIM / OBSERVE / REJECT
→ existing risk or execution stack
```

The discovery question is:

> **When your trading agent sees an opportunity, how do you verify it is still executable before letting it act?**

### 2. Quant and trading-infrastructure teams

Teams that want an independent replay and pre-trade verification layer without handing over strategy ownership. RESONANCE verifies the candidate while the team keeps its alpha logic private.

### 3. Financial-agent infrastructure

Programmable-wallet, treasury, payment and autonomous-finance systems where an action should be checked against explicit invariants before execution.

Arbitrage is the first domain, not the limit of the verification model.

## Why this is more than a spread scanner

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

A route reaches `EXECUTE_SIM` only after the deterministic verifier and monotonic regime gate allow it. A later outcome measures whether that confidence was deserved.

The verifier and shadow prediction layers cannot upgrade a failed deterministic decision:

```text
REJECT < OBSERVE < EXECUTE_SIM
final_verdict <= base_verdict
```

## Trust infrastructure underneath the product

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

These layers preserve what was observed, which policy was active, why a decision was allowed, how it performed later and whether the governing policy itself was valid.

## Safety boundary

RESONANCE Verify remains **paper-only**.

It does not:

- place live orders;
- sign transactions;
- store exchange or wallet private keys;
- initiate transfers or bridges;
- allocate live capital;
- provide copy-trading automation;
- guarantee profit;
- treat future public top-of-book prices as executable fills.

Public market adapters use read-only data. Replay, calibration, governance and benchmark layers operate on local evidence artifacts.

## Product roadmap

The next product decision is evidence-driven rather than version-driven.

```text
if partners need a synchronous integration
→ Verify API / SDK

if partners value replay most
→ Replay / Benchmark as a service

if real corpus proves predictive value
→ predictive shadow ranking

if wallet-copyability demand is validated
→ Wallet Intelligence

if enterprise identity assurance is required
→ cryptographic authority attestation
```

The market should choose the next deep research layer.

## Technical documentation

Research details live under `docs/` rather than in the first 30 seconds of the product page.

Key documents:

- `docs/market-data-contracts.md`
- `docs/product-0.1-opportunity-truth-benchmark.md`
- `docs/v0.12-design.md` — stability decomposition
- `docs/v0.13-design.md` — policy promotion
- `docs/v0.14-design.md` — policy lineage and revocation
- `docs/v0.15-design.md` — authority and delegation
- `docs/v0.16.2-design.md` — append-only real-market corpus
- `docs/v0.16.3-design.md` — corpus runner
- `docs/v0.16.4-design.md` — corpus quality gate

## Tests

```bash
pytest
```

Coverage spans route verification, quote provenance, retry identity, truth accounting, replay determinism, anti-lookahead constraints, calibration/validation firewalls, walk-forward stability, governance receipts, corpus quality, unit-safe PnL, tamper rejection and full benchmark reproduction.

---

### Product thesis

**A financial agent should not act merely because it found a signal. It should be able to prove why the proposed action still satisfies its execution invariants.**
