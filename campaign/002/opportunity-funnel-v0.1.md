# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `78ef5935370d4e240dbe4ccfe2cdbca248be96b3acdf76a90aafdf386f862569`
- Replay SHA-256: `180b4fb2db3ddede89e5747ecc134fc2011f9e9036ce469c05862877b038ada1`

## Cumulative funnel

- Captured terminal cycles: **1770**
- Complete evidence: **1766** (99.77%)
- Structural constraints pass: **1468** (82.94%)
- Gross-positive before costs: **213** (12.03%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -4.26 bps (min -40.61, max 10.88)**
- Expected net edge: **mean -40.20 bps (min -76.42, max -25.12)**
- Observed terminal edge: **mean -40.12 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.81, max 36.00)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 1255 × `GROSS_NON_POSITIVE`
- 213 × `MODELED_COSTS_ERASE_EDGE`
- 172 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 64 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 62 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 4 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `8a38f3df438a1dd559918287f7c5041868aa9bb1cd8bf0e55f420a2fb4b6e6b2`
