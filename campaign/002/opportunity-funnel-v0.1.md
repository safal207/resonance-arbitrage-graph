# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `a894f427339434a761d8f1e3e5007eb25fc5f8151ceede03613806890cf854df`
- Replay SHA-256: `4ef83736aabd717fdffb3b5d7957de865ee12e5dfc6327c3967284e035257dd6`

## Cumulative funnel

- Captured terminal cycles: **1200**
- Complete evidence: **1198** (99.83%)
- Structural constraints pass: **993** (82.75%)
- Gross-positive before costs: **170** (14.17%)
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

- 823 × `GROSS_NON_POSITIVE`
- 170 × `MODELED_COSTS_ERASE_EDGE`
- 123 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 43 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 39 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `47ece96aabcc8b2cb603d888408cb04eee997d0cab5dd7b79efcfb8f337cf2c1`
