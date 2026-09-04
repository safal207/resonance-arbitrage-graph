# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `6cf26c8ef19f9f2dde9c0477d5f3c269c5fe03f4d646681b9404ad6913a7fac3`
- Replay SHA-256: `6e0e4ba9f2840b62483b3fe91b9f950c82e5417b6a2a6e62b5bf5b0ca0abae97`

## Cumulative funnel

- Captured terminal cycles: **400**
- Complete evidence: **398** (99.50%)
- Structural constraints pass: **349** (87.25%)
- Gross-positive before costs: **51** (12.75%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -4.00 bps (min -29.56, max 8.52)**
- Expected net edge: **mean -39.94 bps (min -65.41, max -27.47)**
- Observed terminal edge: **mean -39.95 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.85, max 35.99)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 298 × `GROSS_NON_POSITIVE`
- 51 × `MODELED_COSTS_ERASE_EDGE`
- 26 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 12 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 11 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `4624b4c22b7a42992ea7ff95b4b01d15a703c4c1d761c993a768b8e7a883a077`
