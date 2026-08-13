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
  -> base verifier verdict
  -> route-bound market regime
  -> monotonic regime execution gate
  -> final paper verdict
  -> quote + rolling-window + regime + gate-bound evidence
  -> opportunity observation
  -> truth metrics
  -> regime-segmented reliability ranking
  -> offline replay + calibration benchmark
  -> chronological holdout
  -> joint execute/volatility causal calibration
  -> untouched out-of-sample validation
```

A price difference is not treated as an opportunity by itself. The core invariant is:

```text
final simulated capital > initial capital
AND route returns to its starting asset/venue state
AND quotes are fresh
AND capacity is sufficient
AND route latency is within policy
AND modeled execution/settlement confidence is acceptable
AND final post-regime verdict never exceeds the base verifier verdict
```

## v0.10 — Joint Causal Holdout Calibration

v0.10 jointly calibrates the two thresholds that now change the actual paper decision population:

```text
execute_net_edge_bps × volatile_return_bps
```

The volatility threshold only became causally active after v0.9 introduced the regime execution gate.

For every logical operation, v0.10 evaluates three counterfactual paths:

```text
baseline
  = baseline execute + baseline volatility

execute-only
  = candidate execute + baseline volatility

candidate
  = candidate execute + candidate volatility
```

This separates:

- execute-caused final-verdict changes;
- volatility-caused regime-label changes;
- volatility-caused **final-verdict** changes;
- total final-verdict changes from the joint pair.

A regime relabel is not enough. If changing the volatility threshold turns `NORMAL` into `VOLATILE` while the base verifier is already `OBSERVE`, the final decision remains `OBSERVE`; that produces label support but **zero volatility causal support** and cannot qualify the candidate.

Core v0.10 invariants:

- calibration and validation remain strictly chronological by `logical_operation_id`;
- retries never cross split boundaries;
- validation never chooses among candidate pairs;
- all untuned engine/regime fields, full `RegimeExecutionPolicy`, and rolling-window policy remain frozen;
- baseline execute and volatility thresholds must be uniform across the corpus;
- joint volatility calibration requires `NORMAL -> ALLOW` and a suppressive `VOLATILE -> OBSERVE_ONLY/REJECT` gate;
- causal-support counts are eligibility guardrails, not score rewards;
- validation can explicitly fail for insufficient out-of-sample causal support;
- reports are canonical JSON + SHA-256 and remain advisory/paper-only.

Offline joint holdout CLI:

```bash
resonance-joint-holdout-calibration replay-bundle.json \
  --validation-fraction 0.30 \
  --execute-threshold-bps 25,30,35,40 \
  --volatile-threshold-bps 20,40,60,75 \
  --min-calibration-operations 20 \
  --min-validation-operations 10 \
  --min-calibration-truth-events 10 \
  --min-validation-truth-events 5 \
  --min-truth-lower-bound 0.60 \
  --min-survival-lower-bound 0.70 \
  --min-calibration-execute-causal-changes 1 \
  --min-calibration-volatility-causal-changes 1 \
  --min-validation-execute-causal-changes 1 \
  --min-validation-volatility-causal-changes 1
```

These numbers are examples only. Guardrails are explicit caller inputs rather than hidden trading recommendations.

## v0.9 — Evidence-Bound Regime Execution Gate

v0.9 makes the derived market regime causally active while keeping the system paper-only.

```text
base verifier verdict
  -> evidence-derived rolling regime
  -> explicit regime action
  -> monotonic downgrade
  -> final paper verdict
```

Verdict order:

```text
REJECT < OBSERVE < EXECUTE_SIM
```

Invariant:

```text
final_verdict <= base_verdict
```

Default regime actions:

```text
NORMAL          -> ALLOW
VOLATILE        -> OBSERVE_ONLY
THIN_LIQUIDITY  -> OBSERVE_ONLY
DISLOCATED      -> OBSERVE_ONLY
UNKNOWN         -> REJECT
```

`UNKNOWN` is structurally fail-closed and cannot be configured to allow execution. A base `REJECT` can never be promoted, and a base `OBSERVE` can never become `EXECUTE_SIM`.

Evidence exposes `base_verdict` and final `verdict` separately and binds the gate action, full canonical `RegimeExecutionPolicy`, and gate-policy SHA-256. Observation memory validates the gate against the bound policy before accepting the receipt and classifies outcomes from the **final** verdict. Therefore a regime-downgraded `OBSERVE` does not enter the Opportunity Truth Rate denominator.

Replay artifacts use schema v0.2. Replay rebuilds the route, recomputes the base verifier verdict, recomputes the rolling regime, reapplies the regime gate, and only then grades the later paper outcome. Gate policy is part of the replay decision fingerprint, so changing regime action semantics across retries is decision drift.

Replay v0.1 artifacts are intentionally not silently reinterpreted as v0.2 because v0.1 did not bind this causal policy.

## v0.8 — Holdout Policy Calibration

v0.8 prevents the causally active execute threshold from being selected and graded on the same replay history.

```text
replay corpus
  -> logical-operation groups
  -> strict chronological split
  -> calibration bundle
  -> execute-threshold grid
  -> calibration-only selection
  -> freeze candidate
  -> untouched validation bundle
  -> out-of-sample gate
```

Core holdout invariants:

- splitting happens by `logical_operation_id`, never raw retry rows;
- all attempts for one logical operation remain on one side of the split;
- validation is strictly later than calibration;
- candidate selection sees calibration only;
- validation can pass/fail the selected candidate but cannot choose a fallback;
- all untuned `Policy` fields, full `RegimePolicy`, full `RegimeExecutionPolicy`, and rolling-window policy remain frozen measurement context;
- uncertainty-sensitive guardrails use Wilson lower bounds rather than raw ratios alone;
- insufficient corpus/calibration/validation fails closed explicitly;
- the final report binds corpus/subset SHA-256 values, split membership, grid, evaluations, selected candidate and validation result;
- all results remain advisory and paper-only.

Offline holdout CLI:

```bash
resonance-holdout-calibration replay-bundle.json \
  --validation-fraction 0.30 \
  --execute-threshold-bps 20,30,40,50 \
  --min-calibration-operations 20 \
  --min-validation-operations 10 \
  --min-calibration-truth-events 10 \
  --min-validation-truth-events 5 \
  --min-truth-lower-bound 0.60 \
  --min-survival-lower-bound 0.70 \
  --confidence-z 1.96
```

## v0.7 — Market-State Replay & Calibration Benchmark

v0.7 turns captured v0.6 market state into an offline calibration laboratory. v0.9 upgrades the replay case/bundle/report wire schema to v0.2 so gate policy is part of the decision state.

A `ReplayCase` stores the exact quote snapshots, rolling windows, route-leg descriptors, verifier/regime/gate policies and a later paper outcome. It deliberately does **not** store a trusted final verdict or regime. Replay rebuilds route edges from the captured quotes and recomputes the decision chain.

Core replay invariants:

- future snapshots or rolling samples cannot leak into an earlier decision;
- bundle payloads are canonical JSON and SHA-256 verified before replay;
- retries share one `logical_operation_id`, contiguous attempts and one stable decision fingerprint;
- a terminal attempt cannot be retried;
- retries collapse to one logical operation before metrics;
- incomplete rolling evidence derives `UNKNOWN`, and the default v0.9 gate fails closed to final `REJECT`;
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

Inputs include route-bound spread, capacity ratio, quote freshness/dispersion, cross-rate dislocation and rolling return volatility. `UNKNOWN` fails closed for reliability ranking and, since v0.9, for the final paper execution verdict.

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

The scanner synchronously collects public rolling samples before evaluating opportunities. Each opportunity exposes `base_verdict`, `market_regime`, `regime_action`, and `final_verdict`; `verdict` remains a compatibility alias for the final post-gate verdict. Fee/slippage and rolling-window settings are paper-model assumptions, not claims about an exchange account or universally optimal parameters.

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
  -> regime action + final verdict + gate-policy SHA
  -> replay bundle + calibration report SHA
  -> chronological holdout evidence
  -> joint candidate + causal-support + untouched-validation evidence
```

The observation layer recomputes evidence digests before admitting outcomes to memory and validates the evidence-bound regime gate against its policy. Replay verifies raw bundle digests and reconstructs typed cases. Holdout binds the source corpus, chronological subset digests, frozen measurement context, explicit guardrails, calibration-only selection and untouched validation result into deterministic report envelopes.

## Why cross-venue is observe-only

Buying on venue A and selling on venue B does not return capital to the same venue state. Calling that an executable cycle without modeling inventory/rebalance would hide a real state transition. Future transfer/rebalance edges must model availability, fees, latency, capacity and settlement probability before cross-venue execution can become `EXECUTE_SIM`.

## Tests

```bash
pytest
```

Coverage includes verifier/replay/idempotency contracts, quote provenance, adapters, triangular graph scans, evidence tamper rejection, retry identity, truth metrics, Bayesian reliability, regime isolation, rolling-window ordering/provenance/tail binding, monotonic regime-gate matrices, gate-policy evidence binding, final-verdict truth accounting, replay gate recomputation, gate-policy retry drift, lookahead rejection, replay-bundle tamper detection, deterministic calibration reports, chronological holdout anti-leakage, validation-selection firewall, frozen regime/gate context, Wilson guardrails, joint execute/volatility counterfactual support, label-vs-action causal checks, out-of-sample causal-support gates and report tamper detection.

## Safety boundary

The system remains paper-only. Market data is public GET-only; replay and holdout consume local files only. There is no private API-key handling, account endpoint, order endpoint, signing, wallet interaction, transfer/bridge path, daemon or live execution.

See:

- `docs/market-data-contracts.md`
- `docs/v0.2-design.md`
- `docs/v0.3-design.md`
- `docs/v0.4-design.md`
- `docs/v0.5-design.md`
- `docs/v0.6-design.md`
- `docs/v0.7-design.md`
- `docs/v0.8-design.md`
- `docs/v0.9-design.md`
- `docs/v0.10-design.md`
- Issue #19 — v0.10 Joint Causal Holdout Calibration
