# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `7ce444ad04b161e500f2afa9ff3cc6c6f678d0911b5e62cdbf0dab81f6fef0e0`
- Replay SHA-256: `81fadb554279c96d904a95448af4f302d9e9e64840806be0a032a463cf14ffa5`

## Cumulative funnel

- Captured terminal cycles: **878**
- Complete evidence: **876** (99.77%)
- Structural constraints pass: **744** (84.74%)
- Gross-positive before costs: **129** (14.69%)
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

- 615 × `GROSS_NON_POSITIVE`
- 129 × `MODELED_COSTS_ERASE_EDGE`
- 81 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 27 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 24 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `b972c9e22d98b8d9f175493f59e6584722a8bdf7b8fd80828ec5807caa2b3a16`
