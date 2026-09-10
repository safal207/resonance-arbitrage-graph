# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `c9e75b0c5049baa2382f95bff1c7bc15783b199b9569a1fc791e179fc94995c3`
- Replay SHA-256: `bfdc3516d5cb742a89a3fa8aac2aae16c67c9fb0948c39d571acbe15fb5490c2`

## Cumulative funnel

- Captured terminal cycles: **828**
- Complete evidence: **826** (99.76%)
- Structural constraints pass: **699** (84.42%)
- Gross-positive before costs: **122** (14.73%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -3.90 bps (min -35.06, max 8.52)**
- Expected net edge: **mean -39.85 bps (min -70.89, max -27.47)**
- Observed terminal edge: **mean -39.81 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.83, max 35.99)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 577 × `GROSS_NON_POSITIVE`
- 122 × `MODELED_COSTS_ERASE_EDGE`
- 76 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 27 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 24 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `63461ecc4a002584a6a2191136f0e8f5482a191b6861fbd5f6e2c48996de1919`
