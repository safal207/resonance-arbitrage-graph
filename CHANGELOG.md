# Changelog

## v0.11.0 (in development)

- Add expanding temporal walk-forward folds around the v0.10 joint execute/volatility calibration engine.
- Add strict outcome-availability boundaries: every calibration outcome must be observed before the first validation decision in that fold.
- Keep all attempts of one logical operation together and use the latest outcome-availability timestamp across attempts.
- Reuse the exact v0.10 symmetric 2×2 causal-support, truth/survival, candidate-selection and untouched-validation semantics inside every fold.
- Force each nested v0.10 split to the preplanned walk-forward calibration/validation geometry while keeping all non-split guardrails frozen.
- Count failed/sparse fold validation in the temporal denominator instead of silently dropping it.
- Add validation pass-rate, selected-policy coverage, unique-policy, policy-switch-rate and threshold-range stability metrics.
- Add explicit `PASSED_STABILITY`, `INSUFFICIENT_CORPUS`, `INSUFFICIENT_FOLDS` and `UNSTABLE` statuses.
- Bind fold plan, source/tail operation order, outcome-availability timestamps, nested v0.10 envelopes and aggregate metrics into deterministic SHA-256 evidence.
- Add semantic envelope verification plus deterministic replay-bundle reproduction verification.
- Add offline `resonance-walk-forward-stability` CLI and package version 0.11.0.

## v0.10.0

- Add joint calibration of causally active `execute_net_edge_bps` and `volatile_return_bps` thresholds.
- Add symmetric 2×2 counterfactual causal-support accounting across baseline, execute-only, volatility-only, and joint candidate decisions.
- Attribute execute support while holding candidate volatility fixed, and volatility support while holding candidate execute fixed.
- Distinguish regime-label changes from actual final-verdict changes so label-only volatility effects cannot qualify a candidate.
- Require explicit calibration/validation causal-support floors for execute and volatility dimensions.
- Keep causal support as an eligibility guard rather than rewarding candidates merely for changing more decisions.
- Preserve the chronological validation-selection firewall: validation can pass/fail only the calibration winner and cannot select a fallback.
- Freeze all untuned engine/regime fields, full `RegimeExecutionPolicy`, rolling-window policy, and baseline tuned values across the corpus.
- Recursively freeze joint policy context and independently verify its inner SHA-256 against forged measurement-context mutation.
- Add deterministic joint holdout report evidence with source/subset digests, candidate grid, 2×2 result digests, causal-support counts, selected pair, and untouched validation result.
- Add offline `resonance-joint-holdout-calibration` CLI and package version 0.10.0.

## v0.9.0

- Add monotonic regime execution gate after the base verifier: derived market regime can preserve or downgrade a verdict, never upgrade it.
- Add explicit `RegimeExecutionPolicy` with fail-closed `UNKNOWN -> REJECT` and default `VOLATILE/THIN_LIQUIDITY/DISLOCATED -> OBSERVE_ONLY` behavior.
- Separate base verifier verdict from final post-gate verdict in paper evidence and live scan output.
- Bind regime action, final verdict, gate policy and gate-policy SHA-256 into rolling market evidence.
- Make observation memory validate the evidence-bound gate and classify outcomes from the final post-gate verdict.
- Upgrade replay artifacts to schema v0.2, bind gate policy into the decision fingerprint, and recompute base verdict -> regime -> gate -> final verdict during replay.
- Include regime execution policy in the holdout frozen policy context so incompatible gate semantics cannot be blended.
- Add regression coverage for the full monotonic verdict matrix, gate-policy digest changes, memory truth-denominator behavior, replay gate recomputation and retry policy drift.

## v0.8.0

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
- Derive route-specific spread, capacity ratio, freshness and cross-rate-dislocation features from exact quote provenance.
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
