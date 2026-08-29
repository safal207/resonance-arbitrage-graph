# Product 0.2 — Corpus Campaign 002 measurement contract

Campaign 001 is preserved as an append-only diagnostic corpus. Its first 24 terminal operations exposed a measurement-contract defect: Kraken per-level update timestamps were treated as current REST-snapshot timestamps, rolling coverage was jitter-sensitive, and immediate two-leg buy/sell round trips consumed candidate slots. Campaign 001 must not be used for a public Opportunity Truth claim.

Campaign 002 starts from a new dedicated corpus and data branch. It changes the measurement contract without rewriting Campaign 001 evidence.

## Frozen inputs

- Kraken public `PreTrade` snapshots;
- paper-only USD-start triangular routes through BTC;
- five normal profiles at USD 25;
- one explicit USD 250,000 capacity-stress negative control;
- 10 bps fee + 2 bps slippage per leg;
- 5 bps minimum post-cost `EXECUTE_SIM` edge;
- 60-second outcome horizon;
- maximum three route hops;
- immediate inverse two-leg round trips excluded from opportunity candidates;
- six rolling samples, nominal one-second interval;
- 10-second rolling horizon and 50% minimum coverage.

## Why the normal amount is USD 25

The campaign is measuring route economics and edge survival, not attempting to prove a large executable size from one top-of-book level. The normal micro-notional reduces systematic capacity rejection on thin cross pairs. Capacity remains explicitly tested through the separate stress profile and remains part of every route verdict.

## Timestamp rule

Kraken `publication_ts` describes when a price level was last updated and published. Campaign 002 uses the time the REST snapshot was observed by the verifier as hard quote freshness. It does not reinterpret a resting level's update time as evidence that the newly fetched snapshot itself is stale.

## Claim gates unchanged

Campaign 002 does not lower any benchmark or publication gate:

- at least 100 terminal logical operations;
- at least 30 determinate TP+FP truth events;
- at least 20 distinct decision batches and 10 effective batches;
- at least one hour of temporal coverage;
- route, market and regime diversity gates;
- full corpus/report source reproduction;
- manual publication review after automated internal readiness.

## Safety boundary

Public market data and paper evaluation only. No credentials, private exchange APIs, wallet signing, orders, transfers, live capital, automatic policy promotion or profitability guarantee.
