# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `343c02e6f6c1a440aa5ed68ecff32ac91778491f48378880aefa010bdd7a5b73`
- Replay SHA-256: `716de7e67c33bcac6bffbb72e2155c4547639416b4587fa8234649e148cfdb79`

## Cumulative funnel

- Captured terminal cycles: **440**
- Complete evidence: **438** (99.55%)
- Structural constraints pass: **382** (86.82%)
- Gross-positive before costs: **57** (12.95%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -3.97 bps (min -29.56, max 8.52)**
- Expected net edge: **mean -39.91 bps (min -65.41, max -27.47)**
- Observed terminal edge: **mean -39.93 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.85, max 35.99)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 325 × `GROSS_NON_POSITIVE`
- 57 × `MODELED_COSTS_ERASE_EDGE`
- 29 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 14 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 13 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `46dbfb6c18808dd56f8448a99606b09d9b708f31f26ad8e6c6c59c43f243145f`
