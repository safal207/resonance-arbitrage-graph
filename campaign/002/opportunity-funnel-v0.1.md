# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `1b54588612fba6cb4df9f1558084c792700863a0865c3ac7000471a6c111fbdc`
- Replay SHA-256: `0bd8118240788ecc76fa90230dc4460211b80ac6f40b7c38e82a0ed7cca73344`

## Cumulative funnel

- Captured terminal cycles: **1160**
- Complete evidence: **1158** (99.83%)
- Structural constraints pass: **966** (83.28%)
- Gross-positive before costs: **167** (14.40%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -3.93 bps (min -35.06, max 8.52)**
- Expected net edge: **mean -39.87 bps (min -70.89, max -27.47)**
- Observed terminal edge: **mean -39.81 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.83, max 35.99)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 799 × `GROSS_NON_POSITIVE`
- 167 × `MODELED_COSTS_ERASE_EDGE`
- 118 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 39 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 35 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `171f8ae70e4b2c9299c4f0d77467a252d1f4acd55a1e9e22946ace9af01fd6fc`
