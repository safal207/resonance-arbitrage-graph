# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `99410811e59839f966dfcd09b1005b6cadbdfd246956436cfefbd4d73d85eae7`
- Replay SHA-256: `c0ea80f873d246daa62b544fb0f0da5b54c2b88324269c35997be372202d08ff`

## Cumulative funnel

- Captured terminal cycles: **590**
- Complete evidence: **588** (99.66%)
- Structural constraints pass: **508** (86.10%)
- Gross-positive before costs: **86** (14.58%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -3.86 bps (min -35.06, max 8.52)**
- Expected net edge: **mean -39.80 bps (min -70.89, max -27.47)**
- Observed terminal edge: **mean -39.80 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.83, max 35.99)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 422 × `GROSS_NON_POSITIVE`
- 86 × `MODELED_COSTS_ERASE_EDGE`
- 42 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 20 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 18 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `6e9ade46d977a1fe862a81161dc3d0646efafdd179e5d8c490ccd2562bd0712f`
