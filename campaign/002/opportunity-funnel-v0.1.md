# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `2746b6c029dd8804dddf55d97ba2e1b4765517b4f563387dd21f59f2e8296bdd`
- Replay SHA-256: `7e960fb3197fc6e9c036a0d6bb5c36ace75e12c6d108bce4a39ea9a3748e9f9c`

## Cumulative funnel

- Captured terminal cycles: **1740**
- Complete evidence: **1736** (99.77%)
- Structural constraints pass: **1442** (82.87%)
- Gross-positive before costs: **210** (12.07%)
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

- 1232 × `GROSS_NON_POSITIVE`
- 210 × `MODELED_COSTS_ERASE_EDGE`
- 168 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 64 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 62 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 4 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `aefab026a3e261d23464eaa6d5aa4b9883030222295e6f98f37701d01be92039`
