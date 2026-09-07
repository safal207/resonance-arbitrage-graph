# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `43b8336e3c1ba28b9343049867d7a78a4f0b7a9fb35899e80bc6d880d4e77150`
- Replay SHA-256: `477393c0e6f46f551176d701a58f4dc809190ab06c8aa451c5894f3816c9395e`

## Cumulative funnel

- Captured terminal cycles: **620**
- Complete evidence: **618** (99.68%)
- Structural constraints pass: **533** (85.97%)
- Gross-positive before costs: **92** (14.84%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -3.88 bps (min -35.06, max 8.52)**
- Expected net edge: **mean -39.82 bps (min -70.89, max -27.47)**
- Observed terminal edge: **mean -39.80 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.83, max 35.99)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 441 × `GROSS_NON_POSITIVE`
- 92 × `MODELED_COSTS_ERASE_EDGE`
- 44 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 23 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 18 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `5bf8d6c599e0a3e0edfe8b228d635a428fc28e8e616032a4927e41804b7d6cb7`
