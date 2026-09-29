# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `14a34de29987a2e9a70fe115a63c0411fdf6c8cb7027b02d84c540ebcc6cc614`
- Replay SHA-256: `b0d7655df12420ac1de3b0c825c8362ce2deed83bc468ae4ce88503e15829804`

## Cumulative funnel

- Captured terminal cycles: **2000**
- Complete evidence: **1994** (99.70%)
- Structural constraints pass: **1658** (82.90%)
- Gross-positive before costs: **226** (11.30%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -4.27 bps (min -40.61, max 10.88)**
- Expected net edge: **mean -40.21 bps (min -76.42, max -25.12)**
- Observed terminal edge: **mean -40.14 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.81, max 36.00)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 1432 × `GROSS_NON_POSITIVE`
- 226 × `MODELED_COSTS_ERASE_EDGE`
- 192 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 73 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 71 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 6 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `f6635f8908039cb029268499e8523050c9dbcf667af08d1784656a10ac80c34f`
