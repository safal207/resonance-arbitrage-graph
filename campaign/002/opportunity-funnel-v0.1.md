# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `0e90bf6aab2f4906c104ea4463d78c2db30e0274283f36b0dc1d30899c3ae86e`
- Replay SHA-256: `137642bdae2712bae9079aacf5f190cf9690bae1925ab3f052630bc3b5021362`

## Cumulative funnel

- Captured terminal cycles: **1550**
- Complete evidence: **1548** (99.87%)
- Structural constraints pass: **1293** (83.42%)
- Gross-positive before costs: **199** (12.84%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -4.20 bps (min -40.61, max 10.88)**
- Expected net edge: **mean -40.14 bps (min -76.42, max -25.12)**
- Observed terminal edge: **mean -40.04 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.81, max 36.00)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 1094 × `GROSS_NON_POSITIVE`
- 199 × `MODELED_COSTS_ERASE_EDGE`
- 149 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 55 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 51 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `4200c561c09a685b1bb175439ffb7065018676ac3360b3c0d042a8330fbdcf85`
