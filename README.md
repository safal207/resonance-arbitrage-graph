# RESONANCE Arbitrage Graph

A paper-only causal verification engine for crypto-arbitrage opportunities.

The project does **not** place live orders, sign transactions, hold exchange keys, or transfer funds. Its job is to decide whether a visible market discrepancy still looks executable after modeling costs, liquidity, freshness, latency, settlement risk, market regime and historical signal reliability — and to emit deterministic evidence and outcome memory for that decision.

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
  -> state transitions
  -> settlement assumptions
  -> paper PnL
  -> quote + rolling-window + regime-bound evidence
  -> opportunity observation
  -> truth metrics
  -> regime-segmented reliability ranking
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

## v0.6 — Evidence-Bound Rolling Market State

v0.6 removes caller-supplied volatility from the live paper path. The scanner samples public GET-only market data into deterministic rolling windows and derives short-window volatility from the observed mid-price returns.

A rolling window is scoped to one exact:

```text
venue + symbol + base_asset + quote_asset
```

Each sample preserves bid/ask price and quantity, observation time, timestamp class, optional exchange timestamp, freshness reference, source URL and metadata URL.

Important invariants:

- input samples must already be strictly timestamp ordered;
- duplicate/reordered timestamps are rejected rather than silently sorted;
- all samples in a window must belong to the same exact market;
- minimum sample count and time coverage are explicit `RollingWindowPolicy` fields;
- incomplete window evidence yields `UNKNOWN`, never guessed `NORMAL`;
- the final sample of every route-bound window must exactly equal the current `QuoteSnapshot` backing that route;
- the exact canonical window, summary and SHA-256 are bound into final evidence.

Volatility is derived as the population standard deviation of consecutive mid-price returns in basis points. It is not annualized, so the sampling cadence and window policy are part of the evidence-bearing assumptions.

For multi-leg routes, v0.6 conservatively uses the maximum derived volatility among the exact markets bound to the route.

## v0.5 — Regime-Aware Calibration

v0.5 derives a market regime for each paper route and binds that regime into evidence before reliability history can use it.

Regimes:

```text
NORMAL
VOLATILE
THIN_LIQUIDITY
DISLOCATED
UNKNOWN
```

The feature vector is route-specific:

- maximum normalized spread across the snapshots actually bound to the route;
- minimum leg capacity ratio, computed in each edge's own source-asset units;
- maximum quote age and quote-age dispersion;
- cross-rate dislocation derived from the product of raw route rates;
- short-window return volatility.

Classification precedence is deterministic:

```text
freshness failure -> UNKNOWN
DISLOCATED
THIN_LIQUIDITY
missing volatility -> UNKNOWN
VOLATILE
NORMAL
```

A route cannot be called `NORMAL` without volatility evidence. v0.5 exposed an explicit lower-level volatility input; v0.6 replaces that input in the live scanner with an evidence-bound rolling window.

`make_regime_market_evidence_receipt(...)` binds route-derived features, feature provenance, reasons and `RegimePolicy` thresholds. `make_window_regime_evidence_receipt(...)` is the stronger v0.6 path: volatility provenance is `derived_from_rolling_window` and the full window evidence is included in the final digest.

Observation memory inherits `regime`, `regime_features` and `regime_reasons` from a regime-bound receipt and rejects caller attempts to relabel evidence into a different regime.

## v0.4 — Reliability-Adjusted Ranking

v0.4 uses v0.3 outcome memory to rank new paper-only opportunities by observed reliability rather than raw spread alone.

- `ReliabilityProfile` collapses retries by `logical_operation_id` and segments history by exact `route_id` plus caller-selected market context (default: `venue`, `regime`).
- Opportunity Truth Rate and Route Survival Rate use Bayesian Beta priors so tiny samples cannot imply extreme confidence.
- Historical prediction error may only reduce the current edge: positive historical error never increases a new signal.
- `history_confidence` grows with matching evidence and is capped at 1.0.
- `ReliabilityAdjustedScore` exposes raw edge, bias penalty, bias-adjusted edge, truth probability, survival probability, history confidence, provisional score and final score.
- `INSUFFICIENT_HISTORY` candidates remain observable but do not receive a trusted final ranking score.
- A positive verifier signal can be `SUPPRESSED_BY_HISTORY` when historical overprediction consumes its edge.
- Non-positive raw edge and any verifier verdict other than `EXECUTE_SIM` remain `INELIGIBLE`.
- Cross-venue `OBSERVE_ONLY_REBALANCE_UNMODELED` is never promoted by historical reliability.

Default score for sufficiently evidenced candidates:

```text
adjusted_score_bps
  = bias_adjusted_edge_bps
    * smoothed_truth_rate
    * smoothed_survival_rate
    * history_confidence
```

This is an advisory paper-ranking score, not realized PnL and not a live-trading instruction.

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
  --max-hops 3 \
  --rolling-samples 5 \
  --rolling-interval-ms 1000 \
  --rolling-horizon-ms 5000 \
  --rolling-min-coverage-ratio 0.8
```

The scanner synchronously collects the rolling samples before evaluating opportunities. It performs public reads only; there is no daemon or trading loop.

`--fee-bps`, `--slippage-bps` and rolling-window settings are **paper-model assumptions**, not claims about your actual exchange account or universally optimal market windows.

Each surfaced cycle includes a logical operation ID, derived market regime, per-market rolling-window SHA/summary, deterministic final evidence SHA-256 and explicit edge-to-snapshot market bindings.

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

`make_regime_market_evidence_receipt(...)` extends that proof with route-derived regime features, explicit feature provenance, classification reasons and policy thresholds.

`make_window_regime_evidence_receipt(...)` additionally binds the exact rolling public samples, their source/timestamp provenance, window policy, per-market digest, summary and current-snapshot tail identity.

The observation layer recomputes the SHA-256 over canonical receipt JSON before admitting it to memory. The reliability layer consumes validated, collapsed observations rather than raw retry rows.

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

Until those edges exist, cross-venue gaps are observations, not `EXECUTE_SIM` routes, and reliability history cannot promote them.

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
- Bayesian low-sample reliability shrinkage
- negative-edge non-promotion
- historical prediction-bias suppression
- route/context segment isolation
- deterministic reliability ranking
- deterministic regime classification and precedence
- route-bound capacity/spread/freshness/dislocation features
- regime-evidence tamper rejection
- evidence-bound observation regime inheritance/conflict rejection
- exact-regime reliability isolation and `UNKNOWN` fail-closed ranking
- rolling-window strict ordering and duplicate rejection
- deterministic rolling-window SHA and derived volatility
- rolling-window price/provenance tamper sensitivity
- current-route snapshot ↔ rolling-window-tail binding
- incomplete rolling-window `UNKNOWN` behavior
- synchronous live rolling collection without network calls in CI

## Safety boundary

The system remains paper-only. The market-data layer implements GET-only public data. There is no private API-key handling, signing, account endpoint, order endpoint, wallet interaction, or fund-transfer path.

See:

- `docs/market-data-contracts.md`
- `docs/v0.2-design.md`
- `docs/v0.3-design.md`
- `docs/v0.4-design.md`
- `docs/v0.5-design.md`
- `docs/v0.6-design.md`
- Issue #11 — v0.6 Evidence-Bound Rolling Market State
