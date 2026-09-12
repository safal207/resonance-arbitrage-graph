# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `7dd1cdd9fe7a619df8f361d4fb846fb748ba9c25f175d1dddd802d121c19b144`
- Replay SHA-256: `0539269766fb4671496e4cd01878c1b27fef9ddb05d8332f350d445c00f9964f`

## Cumulative funnel

- Captured terminal cycles: **980**
- Complete evidence: **978** (99.80%)
- Structural constraints pass: **828** (84.49%)
- Gross-positive before costs: **147** (15.00%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -3.94 bps (min -35.06, max 8.52)**
- Expected net edge: **mean -39.88 bps (min -70.89, max -27.47)**
- Observed terminal edge: **mean -39.82 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.83, max 35.99)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 681 × `GROSS_NON_POSITIVE`
- 147 × `MODELED_COSTS_ERASE_EDGE`
- 93 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 30 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 27 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `f604eda2045131bf467609d2d1f5a105da2b4ce26db49f2be5dd9ca1802caeb2`
