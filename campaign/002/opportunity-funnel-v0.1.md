# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `35a00be6349f551ef42ddfb9fcf7034e467c7bb80b9bec42aa8549b60cd4c016`
- Replay SHA-256: `5e0daa5e9ec55a1f6336308eec77cbecf692b0069679f07977facb1cbdbf042f`

## Cumulative funnel

- Captured terminal cycles: **1030**
- Complete evidence: **1028** (99.81%)
- Structural constraints pass: **864** (83.88%)
- Gross-positive before costs: **151** (14.66%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -3.91 bps (min -35.06, max 8.52)**
- Expected net edge: **mean -39.85 bps (min -70.89, max -27.47)**
- Observed terminal edge: **mean -39.80 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.83, max 35.99)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 713 × `GROSS_NON_POSITIVE`
- 151 × `MODELED_COSTS_ERASE_EDGE`
- 102 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 33 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 29 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `0a909a212d821e65fc394baec70c285c8e9f9cc954a6897b9b31ae1fa586ec5c`
