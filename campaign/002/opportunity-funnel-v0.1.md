# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `106a6888ba388853d583b46072704b0035dde3d75fd6b577f2a142b0c10b42bb`
- Replay SHA-256: `baf7f1636466c0666632f6f5599ce20d48e2dac81fbe0830683f87de74c416a9`

## Cumulative funnel

- Captured terminal cycles: **460**
- Complete evidence: **458** (99.57%)
- Structural constraints pass: **397** (86.30%)
- Gross-positive before costs: **62** (13.48%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -3.94 bps (min -29.56, max 8.52)**
- Expected net edge: **mean -39.89 bps (min -65.41, max -27.47)**
- Observed terminal edge: **mean -39.89 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.85, max 35.99)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 335 × `GROSS_NON_POSITIVE`
- 62 × `MODELED_COSTS_ERASE_EDGE`
- 30 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 16 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 15 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `99f2cdf7d80bce1756fba8829387d982060f409fe5d9b945625c3cbe287d6fef`
