# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `235afc203dc3350b9962add5cfdea9bc6cb5059b8acf377d00b155c9e64eb631`
- Replay SHA-256: `439cd2c894b8d1840770168a5c9a9dd3dfd3049d8d9fb5840d9a891bb4713943`

## Cumulative funnel

- Captured terminal cycles: **948**
- Complete evidence: **946** (99.79%)
- Structural constraints pass: **801** (84.49%)
- Gross-positive before costs: **142** (14.98%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -3.96 bps (min -35.06, max 8.52)**
- Expected net edge: **mean -39.90 bps (min -70.89, max -27.47)**
- Observed terminal edge: **mean -39.84 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.83, max 35.99)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 659 × `GROSS_NON_POSITIVE`
- 142 × `MODELED_COSTS_ERASE_EDGE`
- 89 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 29 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 27 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `e3a46e80c40685a2735af30c4ed6db0ab720d1c4aa1b30671d7f59a0324c75bd`
