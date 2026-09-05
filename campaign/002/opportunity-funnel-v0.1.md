# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `17e1f1c59515eedabe082039ed034368f8deccc20510050ac3c7cff05b5939d1`
- Replay SHA-256: `725c08159cb0b5bdf0ff1823152f66a25eaf23bdeec40f14122a08d5e66b681c`

## Cumulative funnel

- Captured terminal cycles: **500**
- Complete evidence: **498** (99.60%)
- Structural constraints pass: **431** (86.20%)
- Gross-positive before costs: **70** (14.00%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -3.89 bps (min -29.56, max 8.52)**
- Expected net edge: **mean -39.83 bps (min -65.41, max -27.47)**
- Observed terminal edge: **mean -39.86 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.85, max 35.99)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 361 × `GROSS_NON_POSITIVE`
- 70 × `MODELED_COSTS_ERASE_EDGE`
- 33 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 18 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 16 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `024623210881a49973c68a244196756445db6eb9d4856406517507497c23291f`
