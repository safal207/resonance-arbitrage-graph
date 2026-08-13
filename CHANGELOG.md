# Changelog

## v0.8.0 (in development)

- Add strict chronological holdout splitting by logical operation, keeping retries on one side of the split.
- Add calibration-only search for the causally active verifier execute threshold with untouched out-of-sample validation.
- Keep the full RegimePolicy and rolling-window measurement policy frozen instead of pretending a label-only volatility threshold is an executable-policy tuning dimension.
- Add Wilson lower-bound truth/survival guardrails for uncertainty-sensitive policy evaluation.
- Reject heterogeneous untuned policy/measurement contexts instead of blending incomparable history.
- Bind source/subset digests, split membership, candidate evaluations, selected policy and validation result into deterministic SHA-256 reports.
- Add explicit fail-closed statuses for insufficient corpus/calibration/validation and failed holdout validation.
- Add offline `resonance-holdout-calibration` CLI with caller-supplied guardrails and no network or execution path.

## v0.7.0

- Add deterministic offline replay bundles for captured quote snapshots and rolling windows.
- Recompute route verdicts and market regimes during replay instead of trusting stored labels.
- Add replay-bundle and calibration-report SHA-256 envelopes with tamper detection.
- Collapse retry attempts by logical operation and reject decision-state drift or retry after terminal outcomes.
- Add per-regime and per-route truth/survival/prediction-error calibration reports.
- Add advisory verifier/regime threshold sensitivity analysis.
- Add offline `resonance-replay-benchmark` CLI with no network or live execution path.

## v0.6.0

- Add deterministic evidence-bound rolling market windows for public quote samples.
- Preserve quote source/timestamp provenance and reject reordered or duplicate samples.
- Derive short-window return volatility from rolling mid-price returns instead of caller input.
- Require every rolling window tail to equal the exact current route snapshot.
- Bind rolling-window canonical payloads, summaries and SHA-256 digests into regime evidence.
- Make incomplete rolling evidence fail closed to UNKNOWN.
- Update the public live paper scanner to collect rolling samples synchronously before evaluation.

## v0.5.0

- Add deterministic market regimes: NORMAL, VOLATILE, THIN_LIQUIDITY, DISLOCATED and fail-closed UNKNOWN.
- Derive route-specific spread, capacity, freshness and cross-rate-dislocation features from exact quote provenance.
- Add collision-safe regime market context and reject UNKNOWN in reliability ranking.
- Bind regime features, feature provenance, classification reasons and RegimePolicy thresholds into SHA-256 evidence.
- Emit derived regime from the public read-only live paper scanner.

## v0.4.0

- Add route/context-segmented reliability profiles from v0.3 logical observations.
- Add Bayesian-smoothed Opportunity Truth Rate and Route Survival Rate.
- Apply historical prediction error as a negative-only edge calibration; history cannot manufacture positive edge.
- Add explicit history-confidence and minimum-evidence guards.
- Add deterministic reliability-adjusted ranking with stable tie-breaking.
- Keep non-`EXECUTE_SIM`, non-positive and cross-venue observe-only candidates ineligible.

## v0.3.0

- Add evidence-bound `OpportunityObservation` records.
- Add append-only deterministic JSONL observation journal.
- Preserve one semantic `logical_operation_id` across retry attempts without double-counting.
- Reject duplicate executions, attempt gaps, identity drift and replay after terminal outcomes.
- Add TRUE_POSITIVE, FALSE_POSITIVE, EXPIRED, REJECTED and INDETERMINATE truth classes.
- Add Opportunity Truth Rate, False Opportunity Rate, Route Survival Rate and prediction-error metrics.

## v0.2.0

- Normalize public best-bid/best-ask snapshots.
- Add read-only Binance Spot and Kraken Spot adapters.
- Convert quotes into graph trade edges with explicit cost assumptions.
- Add single-venue live triangular paper scan.
- Keep cross-venue gaps observe-only until rebalance/settlement is modeled.
- Bind public quote provenance into deterministic evidence.

## v0.1.0

- Initial paper-only causal arbitrage verification engine.
