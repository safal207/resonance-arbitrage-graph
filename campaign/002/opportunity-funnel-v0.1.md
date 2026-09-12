# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `020283ea530a2f6b847b70596985282f734dc1919bfc027e8c094d3d37f6faa2`
- Replay SHA-256: `f07ee378ea459871ed1d8f025671101d8c21c9929f86755097724a40ac33a3e9`

## Cumulative funnel

- Captured terminal cycles: **958**
- Complete evidence: **956** (99.79%)
- Structural constraints pass: **808** (84.34%)
- Gross-positive before costs: **144** (15.03%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -3.96 bps (min -35.06, max 8.52)**
- Expected net edge: **mean -39.90 bps (min -70.89, max -27.47)**
- Observed terminal edge: **mean -39.84 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.83, max 35.99)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 664 × `GROSS_NON_POSITIVE`
- 144 × `MODELED_COSTS_ERASE_EDGE`
- 91 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 30 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 27 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `9f33999383db1c1d61a9f89d6365758804f5b4cc03c37ee0095e33f723eb3479`
