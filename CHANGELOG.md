# Changelog

## v0.4.0 (in development)

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
