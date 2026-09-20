# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `75d12b1cf231fa31a54d6bede06ceaa0619bf74318c95798050bc105d34d9440`
- Replay SHA-256: `392b3e3a2a4211552abf02a20ca39cb19071b63c3bb270c26cfea813ffcee450`

## Cumulative funnel

- Captured terminal cycles: **1530**
- Complete evidence: **1528** (99.87%)
- Structural constraints pass: **1275** (83.33%)
- Gross-positive before costs: **196** (12.81%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -4.19 bps (min -40.61, max 10.88)**
- Expected net edge: **mean -40.14 bps (min -76.42, max -25.12)**
- Observed terminal edge: **mean -40.04 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.81, max 36.00)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 1079 × `GROSS_NON_POSITIVE`
- 196 × `MODELED_COSTS_ERASE_EDGE`
- 149 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 54 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 50 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `01554a5181a51f4963d38e94f341de7c73d0180ddc6cf01dfeebe43c4f5deb61`
