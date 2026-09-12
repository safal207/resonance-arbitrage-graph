# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `0cc1466880a5bb706ae061b414ca5078de469cbdeb6ae7c0335b882b90a5a62e`
- Replay SHA-256: `a5b389a9518c21d53104e07b4fc3bd14bd936f71ef9f9ae7df1bf5cef5210722`

## Cumulative funnel

- Captured terminal cycles: **968**
- Complete evidence: **966** (99.79%)
- Structural constraints pass: **816** (84.30%)
- Gross-positive before costs: **145** (14.98%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -3.95 bps (min -35.06, max 8.52)**
- Expected net edge: **mean -39.89 bps (min -70.89, max -27.47)**
- Observed terminal edge: **mean -39.83 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.83, max 35.99)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 671 × `GROSS_NON_POSITIVE`
- 145 × `MODELED_COSTS_ERASE_EDGE`
- 93 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 30 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 27 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `71d60508ec6cb0a5c16cd320da2cda1474d0ce41d7bdbb161f674fd020cc9bd6`
