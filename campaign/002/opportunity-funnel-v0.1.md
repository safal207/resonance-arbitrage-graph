# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `3c4ffaf3b9f4a1c718a3414eea024e8f90b23612b59c5bb19440b9a1046d5f63`
- Replay SHA-256: `7589f99723e0f7c96314f042691d9f4de65035bef8b63e8e5d23a0cf04c7475b`

## Cumulative funnel

- Captured terminal cycles: **1940**
- Complete evidence: **1936** (99.79%)
- Structural constraints pass: **1605** (82.73%)
- Gross-positive before costs: **223** (11.49%)
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

- 1382 × `GROSS_NON_POSITIVE`
- 223 × `MODELED_COSTS_ERASE_EDGE`
- 190 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 71 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 70 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 4 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `7d94f5728cd4456f55ab330e5cd31519017d5435c7c353c25189f262e2247b9c`
