# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `54b60c7e271fb4776d8ae834e1463212714505aef11edc41146106f3275129fd`
- Replay SHA-256: `bd5393b1401ac0aa62fcc0a74f5baec11f66f7bc4ea6d21cd2015f106ee99555`

## Cumulative funnel

- Captured terminal cycles: **1310**
- Complete evidence: **1308** (99.85%)
- Structural constraints pass: **1090** (83.21%)
- Gross-positive before costs: **179** (13.66%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -4.02 bps (min -40.61, max 8.52)**
- Expected net edge: **mean -39.96 bps (min -76.42, max -27.47)**
- Observed terminal edge: **mean -39.88 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.81, max 35.99)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 911 × `GROSS_NON_POSITIVE`
- 179 × `MODELED_COSTS_ERASE_EDGE`
- 129 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 49 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 40 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `f45722c837e6602798b2fc9d8ce4757b124c996185e27b89d5c694588abf5750`
