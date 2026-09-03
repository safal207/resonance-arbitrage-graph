# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `6bdd0498caf654f5636c41ab47a684812ab2b82f6f72e4e8aaf39270da65281e`
- Replay SHA-256: `b00b7c9f3df6647aa0773ada75c347ada2bfc7801d825a8e4673bad05d66fba9`

## Cumulative funnel

- Captured terminal cycles: **360**
- Complete evidence: **358** (99.44%)
- Structural constraints pass: **315** (87.50%)
- Gross-positive before costs: **46** (12.78%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -4.08 bps (min -29.56, max 8.52)**
- Expected net edge: **mean -40.03 bps (min -65.41, max -27.47)**
- Observed terminal edge: **mean -40.01 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.85, max 35.99)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 269 × `GROSS_NON_POSITIVE`
- 46 × `MODELED_COSTS_ERASE_EDGE`
- 21 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 11 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 11 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `df7e9c847c983210069b2779bdb3e28a0256cdb1efd86051d586a14df2ac4b9d`
