# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `990bbe85c8b1d1f771228e8187e67218458fd738761bbfbfcd3d81985969400b`
- Replay SHA-256: `5fa9671850d4e4d6d904b5b66b427ce04062b82ceb99131c71041350ba5ff391`

## Cumulative funnel

- Captured terminal cycles: **210**
- Complete evidence: **210** (100.00%)
- Structural constraints pass: **185** (88.10%)
- Gross-positive before costs: **29** (13.81%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -4.19 bps (min -29.56, max 5.22)**
- Expected net edge: **mean -40.13 bps (min -65.41, max -30.75)**
- Observed terminal edge: **mean -40.21 bps (min -88.73, max -30.80)**
- Modeled cost drag: **mean 35.94 bps (min 35.85, max 35.98)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 156 × `GROSS_NON_POSITIVE`
- 29 × `MODELED_COSTS_ERASE_EDGE`
- 10 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 8 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 7 × `STRUCTURAL:CAPACITY_EXCEEDED:0`

Evidence SHA-256: `e0e81c8c4087ea7ae8ac459871742a4b878b8d48c231d002ea5531f05fefc7ac`
