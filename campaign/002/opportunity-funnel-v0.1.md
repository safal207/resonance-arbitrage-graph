# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `0bcb1cbad921938122bb6525173c5fd1292ca264c49a73d690782a525445e028`
- Replay SHA-256: `fb867e4111f35723949e31e5ddcf99c7c85c912bf92e793cc36a79a008af0146`

## Cumulative funnel

- Captured terminal cycles: **1110**
- Complete evidence: **1108** (99.82%)
- Structural constraints pass: **930** (83.78%)
- Gross-positive before costs: **161** (14.50%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -3.93 bps (min -35.06, max 8.52)**
- Expected net edge: **mean -39.87 bps (min -70.89, max -27.47)**
- Observed terminal edge: **mean -39.82 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.83, max 35.99)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 769 × `GROSS_NON_POSITIVE`
- 161 × `MODELED_COSTS_ERASE_EDGE`
- 112 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 36 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 30 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `f01348f5d86b528fac492cf95551c6e8859be4f3e284e56c0bcaaaab2088577e`
