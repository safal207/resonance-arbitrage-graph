# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `450ac368ea9788e21dd3e3f5764ed4138c5445b9693745bbde6146c5947b7c27`
- Replay SHA-256: `4bb05d8ef5d64ba063cff6050613412edecc3b94b30cdb43f6e8d72a4af8e36b`

## Cumulative funnel

- Captured terminal cycles: **1080**
- Complete evidence: **1078** (99.81%)
- Structural constraints pass: **906** (83.89%)
- Gross-positive before costs: **157** (14.54%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -3.92 bps (min -35.06, max 8.52)**
- Expected net edge: **mean -39.87 bps (min -70.89, max -27.47)**
- Observed terminal edge: **mean -39.82 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.83, max 35.99)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 749 × `GROSS_NON_POSITIVE`
- 157 × `MODELED_COSTS_ERASE_EDGE`
- 109 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 34 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 29 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `f6f7309ceb7a35e6a5286ed4f49a3d130ca9a34012107eccaeec0aa445d1cdf3`
