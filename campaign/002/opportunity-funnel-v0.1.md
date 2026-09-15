# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `fd44e62f5f0d6b1e58f1ecae4ed92b2ae263185e08308faaa6eade549a5f8f1c`
- Replay SHA-256: `e251bb11808949df5cf51a233d1151b09a36a634ea48469bc74400e6e5cd3561`

## Cumulative funnel

- Captured terminal cycles: **1150**
- Complete evidence: **1148** (99.83%)
- Structural constraints pass: **959** (83.39%)
- Gross-positive before costs: **165** (14.35%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -3.93 bps (min -35.06, max 8.52)**
- Expected net edge: **mean -39.87 bps (min -70.89, max -27.47)**
- Observed terminal edge: **mean -39.81 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.83, max 35.99)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 794 × `GROSS_NON_POSITIVE`
- 165 × `MODELED_COSTS_ERASE_EDGE`
- 117 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 39 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 33 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `fb9b21dd4126c9156bed62b562cf6bb0c553bf05e268f8327e6d07165616820f`
