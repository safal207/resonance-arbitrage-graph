# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `96512e263173e07edba7070bc87a1d9e7c3828642ba40543de5d052cc1590e97`
- Replay SHA-256: `8b059975d613491577241730cdeca2f83e91a32aab0bafb793d84e158dc523b7`

## Cumulative funnel

- Captured terminal cycles: **170**
- Complete evidence: **170** (100.00%)
- Structural constraints pass: **153** (90.00%)
- Gross-positive before costs: **25** (14.71%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -4.26 bps (min -29.56, max 5.22)**
- Expected net edge: **mean -40.20 bps (min -65.41, max -30.75)**
- Observed terminal edge: **mean -40.29 bps (min -88.73, max -30.80)**
- Modeled cost drag: **mean 35.94 bps (min 35.85, max 35.98)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 128 × `GROSS_NON_POSITIVE`
- 25 × `MODELED_COSTS_ERASE_EDGE`
- 8 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 6 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 3 × `STRUCTURAL:CAPACITY_EXCEEDED:0`

Evidence SHA-256: `20b7a0170821e3e542c2ca474cc1c5fd3fe15a8cf4f56077905116fcc895494d`
