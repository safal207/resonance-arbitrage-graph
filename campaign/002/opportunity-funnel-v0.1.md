# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `8a783b21d8038818523d6dce2ef7aca4af0dd654dab02fbd31e054fe045caba0`
- Replay SHA-256: `43be9ac8d86b06dc58f36c112a8bab24cd1ce927f9c3c437eabfe37d2571ac0f`

## Cumulative funnel

- Captured terminal cycles: **410**
- Complete evidence: **408** (99.51%)
- Structural constraints pass: **356** (86.83%)
- Gross-positive before costs: **52** (12.68%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -4.02 bps (min -29.56, max 8.52)**
- Expected net edge: **mean -39.96 bps (min -65.41, max -27.47)**
- Observed terminal edge: **mean -39.98 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.85, max 35.99)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 304 × `GROSS_NON_POSITIVE`
- 52 × `MODELED_COSTS_ERASE_EDGE`
- 28 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 13 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 11 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `e629cebf14e20ed52db1ac85a6a65c0d84101c4cf0287669c7eba46b8e1ef9fa`
