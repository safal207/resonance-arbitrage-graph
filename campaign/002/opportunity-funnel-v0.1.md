# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `a272a787ddb1847a09e48443c60b2618fa903d89e81e7fc04ade00ca9aac872d`
- Replay SHA-256: `963557ddc5894bab3f56a1476d2e39178db6cbb58925812ba990b716b833d090`

## Cumulative funnel

- Captured terminal cycles: **1750**
- Complete evidence: **1746** (99.77%)
- Structural constraints pass: **1450** (82.86%)
- Gross-positive before costs: **210** (12.00%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -4.26 bps (min -40.61, max 10.88)**
- Expected net edge: **mean -40.20 bps (min -76.42, max -25.12)**
- Observed terminal edge: **mean -40.13 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.81, max 36.00)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 1240 × `GROSS_NON_POSITIVE`
- 210 × `MODELED_COSTS_ERASE_EDGE`
- 170 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 64 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 62 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 4 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `8a5980b5b9e19e2cabcebb72e908a7c411c47e18959d5d59713c16cffedef990`
