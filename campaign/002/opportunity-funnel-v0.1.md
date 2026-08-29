# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `248b3e64b3c505ee101e3b2eaa565a687a4bbb8d3655515eb863183b4ad58d55`
- Replay SHA-256: `a0c6d66873e2f446ff6d046d6d17bd092fd42d2dce6e2e9a4bf732624153c4bb`

## Cumulative funnel

- Captured terminal cycles: **50**
- Complete evidence: **50** (100.00%)
- Structural constraints pass: **47** (94.00%)
- Gross-positive before costs: **8** (16.00%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -4.08 bps (min -19.95, max 5.22)**
- Expected net edge: **mean -40.02 bps (min -55.84, max -30.75)**
- Observed terminal edge: **mean -40.04 bps (min -57.05, max -30.80)**
- Modeled cost drag: **mean 35.94 bps (min 35.89, max 35.98)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 39 × `GROSS_NON_POSITIVE`
- 8 × `MODELED_COSTS_ERASE_EDGE`
- 2 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 1 × `STRUCTURAL:CAPACITY_EXCEEDED:2`

Evidence SHA-256: `55b0a64f8ee4063bcdd19e883b16148779459f6cbc3b3de3d91866c3eb23ba7f`
