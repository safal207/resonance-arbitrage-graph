# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `94fe63daeda21a6fb40b179055c2ec636d1ef19882f4bcbd610f471ffbb469a0`
- Replay SHA-256: `b69fdd9dea5de5c8590e971d833c637501dc130cdef479035e67c9c1110f4e12`

## Cumulative funnel

- Captured terminal cycles: **1090**
- Complete evidence: **1088** (99.82%)
- Structural constraints pass: **914** (83.85%)
- Gross-positive before costs: **158** (14.50%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -3.93 bps (min -35.06, max 8.52)**
- Expected net edge: **mean -39.88 bps (min -70.89, max -27.47)**
- Observed terminal edge: **mean -39.81 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.83, max 35.99)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 756 × `GROSS_NON_POSITIVE`
- 158 × `MODELED_COSTS_ERASE_EDGE`
- 110 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 35 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 29 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `b6e12de6d22db931609c4e9ca5560cb11a3208939d28c8845d666b1763a7b512`
