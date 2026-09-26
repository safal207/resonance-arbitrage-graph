# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `81add05bec76566c3d47e6903ca65d1cc14779f51e4b52f6edcdc5553a33fc66`
- Replay SHA-256: `df6b5e376522529a67424facb0b2b1b3ae67c3ae91ecfc1c74321a51c5491cd3`

## Cumulative funnel

- Captured terminal cycles: **1870**
- Complete evidence: **1866** (99.79%)
- Structural constraints pass: **1549** (82.83%)
- Gross-positive before costs: **218** (11.66%)
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

- 1331 × `GROSS_NON_POSITIVE`
- 218 × `MODELED_COSTS_ERASE_EDGE`
- 183 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 68 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 66 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 4 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `5f97655a42600a10e090ecfecba12ec1d7c3df9aed41e3273f0792bc6691c815`
