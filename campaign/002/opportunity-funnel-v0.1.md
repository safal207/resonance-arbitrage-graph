# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `e30e128c4f031c9898570ad8d2c40b9cf599d6e305df6388c808323c206bc3b0`
- Replay SHA-256: `c069988f3d7f346e71a858d22928861207c7d1071bffa963944caea45b6e97d9`

## Cumulative funnel

- Captured terminal cycles: **1480**
- Complete evidence: **1478** (99.86%)
- Structural constraints pass: **1233** (83.31%)
- Gross-positive before costs: **189** (12.77%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -4.11 bps (min -40.61, max 10.88)**
- Expected net edge: **mean -40.05 bps (min -76.42, max -25.12)**
- Observed terminal edge: **mean -39.97 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.81, max 36.00)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 1044 × `GROSS_NON_POSITIVE`
- 189 × `MODELED_COSTS_ERASE_EDGE`
- 143 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 54 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 48 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `46e1114a66299d438bc92e8c361a98b68c964fa4979fff45b5ec09a254789f00`
