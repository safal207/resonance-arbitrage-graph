# RESONANCE Arbitrage Graph

A paper-only causal verification engine for crypto-arbitrage opportunities.

The project does **not** place live orders, sign transactions, hold exchange keys, or transfer funds. Its job is to decide whether a visible market discrepancy still looks executable after modeling costs, liquidity, freshness, latency, settlement risk, market regime and historical signal reliability — and to emit deterministic evidence, replayable market state and outcome memory for that decision.

## Causal spine

```text
public/fixture market state
  -> normalized quote snapshot
  -> verified pair metadata
  -> rolling public market window
  -> discrepancy
  -> candidate route
  -> execution constraints
  -> route-bound market regime
  -> paper PnL
  -> quote + rolling-window + regime-bound evidence
  -> opportunity observation
  -> truth metrics
  -> regime-segmented reliability ranking
  -> offline replay + calibration benchmark
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

## v0.7 — Market-State Replay & Calibration Benchmark

v0.7 turns captured v0.6 market state into an offline calibration laboratory.

A `ReplayCase` stores the exact quote snapshots, rolling windows, route-leg descriptors, verifier/regime policies and a later paper outcome. It deliberately does **not** store a trusted verdict or regime. Replay rebuilds route edges from the captured quotes, recomputes `evaluate_route(...)`, recomputes the rolling-window market regime, and only then compares the prediction with the later paper result.

Core replay invariants:

- future snapshots or rolling samples cannot leak into an earlier decision;
- bundle payloads are canonical JSON and SHA-256 verified before replay;
- retries share one `logical_operation_id`, contiguous attempts and one stable decision fingerprint;
- a terminal attempt cannot be retried;
- retries collapse to one logical operation before metrics;
- incomplete rolling evidence makes an otherwise executable/observable replay `INDETERMINATE`;
- calibration is segmented by derived regime and semantic route ID;
- threshold sensitivity is advisory only and never mutates runtime policy.

Replay CLI:

```bash
resonance-replay-benchmark replay-bundle.json
```

Optional advisory threshold grid:

```bash
resonance-replay-benchmark replay-bundle.json \
  --execute-threshold-bps 20,30,40,50 \
  --volatile-threshold-bps 50,75,100
```

The replay CLI reads local JSON only and performs no network requests.

## v0.6 — Evidence-Bound Rolling Market State

v0.6 removes caller-supplied volatility from the live paper path. The scanner samples public GET-only market data into deterministic rolling windows and derives short-window volatility from observed mid-price returns.

A rolling window is scoped to one exact `venue + symbol + base_asset + quote_asset`. Each sample preserves price/quantity, observation time, timestamp provenance and source identity.

Important invariants:

- input samples must already be strictly timestamp ordered;
- duplicate/reordered timestamps are rejected rather than silently sorted;
- all samples belong to one exact market;
- minimum sample count and time coverage are explicit policy fields;
- incomplete window evidence yields `UNKNOWN`;
- the final sample of every route-bound window must exactly equal the current `QuoteSnapshot` backing that route;
- the exact canonical window, summary and SHA-256 are bound into final evidence.

For multi-leg routes, v0.6 conservatively uses the maximum derived volatility among the exact markets bound to the route.

## v0.5 — Regime-Aware Calibration

Market regimes are derived from route-specific evidence:

```text
NORMAL
VOLATILE
THIN_LIQUIDITY
DISLOCATED
UNKNOWN
```

Inputs include route-bound spread, capacity ratio, quote freshness/dispersion, cross-rate dislocation and rolling return volatility. `UNKNOWN` fails closed for reliability ranking.

## v0.4 — Reliability-Adjusted Ranking

Historical outcome memory ranks paper opportunities by reliability rather than raw spread alone. Bayesian-smoothed truth/survival rates, negative-only prediction-bias correction and history confidence produce an advisory score. History cannot manufacture positive edge or promote a non-`EXECUTE_SIM` route.

## v0.3 — Opportunity Memory & Truth Metrics

`OpportunityObservation` and the append-only JSONL journal preserve logical-operation identity across retries and record:

```text
TRUE_POSITIVE
FALSE_POSITIVE
EXPIRED
REJECTED
INDETERMINATE
```

Metrics:

```text
Opportunity Truth Rate = TP / (TP + FP)
False Opportunity Rate = FP / (TP + FP)
Route Survival Rate = (TP + FP) / (TP + FP + EXPIRED)
Prediction Error = observed_edge_bps - expected_edge_bps
```

## v0.2 — public read-only market data

- normalized public best-bid/best-ask snapshots;
- read-only Binance Spot and Kraken Spot adapters;
- quote-to-edge conversion with explicit cost assumptions;
- single-venue triangular paper scan;
- cross-venue gaps remain observe-only until rebalance/settlement is modeled;
- public quote provenance is bound into deterministic evidence.

### Live paper scan

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
  --max-hops 3 \
  --rolling-samples 5 \
  --rolling-interval-ms 1000 \
  --rolling-horizon-ms 5000 \
  --rolling-min-coverage-ratio 0.8
```

The scanner synchronously collects public rolling samples before evaluating opportunities. Fee/slippage and rolling-window settings are paper-model assumptions, not claims about an exchange account or universally optimal parameters.

## v0.1 — verification core

- market `Node` / `Edge` graph;
- fee, slippage, gas, capacity, freshness, latency and confidence modeling;
- bounded cycle discovery;
- verdicts `EXECUTE_SIM`, `OBSERVE`, `REJECT`;
- deterministic paper executor and replay/idempotency guard;
- ProofPath-style SHA-256 evidence receipts.

## Evidence

Evidence evolves monotonically:

```text
base route evidence
  -> public quote provenance
  -> regime features + policy
  -> rolling-window state + window SHA
  -> replay bundle + calibration report SHA
```

The observation layer recomputes evidence digests before admitting outcomes to memory. The replay layer similarly verifies the raw replay-bundle digest, reconstructs strongly typed cases, requires canonical round-trip equality, and verifies the reconstructed digest again.

## Why cross-venue is observe-only

Buying on venue A and selling on venue B does not return capital to the same venue state. Calling that an executable cycle without modeling inventory/rebalance would hide a real state transition. Future transfer/rebalance edges must model availability, fees, latency, capacity and settlement probability before cross-venue execution can become `EXECUTE_SIM`.

## Tests

```bash
pytest
```

Coverage includes verifier/replay/idempotency contracts, quote provenance, adapters, triangular graph scans, evidence tamper rejection, retry identity, truth metrics, Bayesian reliability, regime isolation, rolling-window ordering/provenance/tail binding, lookahead rejection, replay-bundle tamper detection, retry collapse, deterministic calibration reports and advisory threshold sensitivity.

## Safety boundary

The system remains paper-only. Market data is public GET-only; replay is offline local-file input only. There is no private API-key handling, account endpoint, order endpoint, signing, wallet interaction, transfer/bridge path, daemon or live execution.

See:

- `docs/market-data-contracts.md`
- `docs/v0.2-design.md`
- `docs/v0.3-design.md`
- `docs/v0.4-design.md`
- `docs/v0.5-design.md`
- `docs/v0.6-design.md`
- `docs/v0.7-design.md`
- Issue #13 — v0.7 Market-State Replay & Calibration Benchmark
