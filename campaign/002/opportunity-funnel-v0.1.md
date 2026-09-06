# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `38d96f30dcb9abd87b8759748526dab6e7b3343356c939d1d5501e902389e985`
- Replay SHA-256: `39c5a7e9d7dd592f43265f598f1049823a420c30cfced7e7f84991d46b010f6e`

## Cumulative funnel

- Captured terminal cycles: **570**
- Complete evidence: **568** (99.65%)
- Structural constraints pass: **490** (85.96%)
- Gross-positive before costs: **83** (14.56%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -3.88 bps (min -35.06, max 8.52)**
- Expected net edge: **mean -39.82 bps (min -70.89, max -27.47)**
- Observed terminal edge: **mean -39.81 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.83, max 35.99)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 407 × `GROSS_NON_POSITIVE`
- 83 × `MODELED_COSTS_ERASE_EDGE`
- 41 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 19 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 18 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `272ed08fc86812f26432f3f7ef35561f5635fc989131c07813ace497fe4d07f9`
