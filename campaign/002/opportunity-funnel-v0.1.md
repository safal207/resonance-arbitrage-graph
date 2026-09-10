# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `17903ebb7eaa9e21b40ea8cc0751701ebea00b100e1e838159cf0ae130ddc604`
- Replay SHA-256: `044616f5bb9beb11befeba85b3e4abe1e58bf11d643a281d77d5ae223dc641ee`

## Cumulative funnel

- Captured terminal cycles: **808**
- Complete evidence: **806** (99.75%)
- Structural constraints pass: **685** (84.78%)
- Gross-positive before costs: **121** (14.98%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -3.90 bps (min -35.06, max 8.52)**
- Expected net edge: **mean -39.84 bps (min -70.89, max -27.47)**
- Observed terminal edge: **mean -39.81 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.83, max 35.99)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 564 × `GROSS_NON_POSITIVE`
- 121 × `MODELED_COSTS_ERASE_EDGE`
- 71 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 26 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 24 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `74e320fc38e8843cb840b3388c99785fd46d313d2c03b4ae0cfc10cc5174a346`
