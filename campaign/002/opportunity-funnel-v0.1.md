# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `3aeacce3de987e49ae7c849afe43b69c294ed0551e336e331f223fd09e3c9379`
- Replay SHA-256: `f7828d6c32ac2548d9e976f9cfbcad43702867d2e2b3d1fb72ebf8704957c949`

## Cumulative funnel

- Captured terminal cycles: **80**
- Complete evidence: **80** (100.00%)
- Structural constraints pass: **73** (91.25%)
- Gross-positive before costs: **13** (16.25%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -3.87 bps (min -19.95, max 5.22)**
- Expected net edge: **mean -39.81 bps (min -55.84, max -30.75)**
- Observed terminal edge: **mean -39.88 bps (min -57.05, max -30.80)**
- Modeled cost drag: **mean 35.94 bps (min 35.89, max 35.98)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 60 × `GROSS_NON_POSITIVE`
- 13 × `MODELED_COSTS_ERASE_EDGE`
- 4 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 2 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 1 × `STRUCTURAL:CAPACITY_EXCEEDED:0`

Evidence SHA-256: `9ca6eef65881ca9fc2c679d9cc071269a1ba4f41007b97ba912ccabbc2d28d13`
