# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `95e4bd22a004a21eeba856a3835d5891376b78c7aa55bb7f4d758c747f41d4df`
- Replay SHA-256: `501501df0430acac1fce14ede235fa4f9cbbb836ff6389350de00e487156a4be`

## Cumulative funnel

- Captured terminal cycles: **1650**
- Complete evidence: **1646** (99.76%)
- Structural constraints pass: **1371** (83.09%)
- Gross-positive before costs: **204** (12.36%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -4.23 bps (min -40.61, max 10.88)**
- Expected net edge: **mean -40.17 bps (min -76.42, max -25.12)**
- Observed terminal edge: **mean -40.10 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.81, max 36.00)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 1167 × `GROSS_NON_POSITIVE`
- 204 × `MODELED_COSTS_ERASE_EDGE`
- 159 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 59 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 57 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 4 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `25943abec00b2b3507fa0708f55a59f08b3ce0dcc9259434adf732ee53cf9842`
