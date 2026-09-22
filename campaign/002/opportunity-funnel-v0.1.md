# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `3543e2f45f0e8d637c0cf59e3edc4f0bdca39c294b649bed5f8f7ffdad1b426e`
- Replay SHA-256: `123ad20b1f6bb965e1cb534ef8caa621a4ee60590db00b13f4b63bac013a7a65`

## Cumulative funnel

- Captured terminal cycles: **1600**
- Complete evidence: **1596** (99.75%)
- Structural constraints pass: **1333** (83.31%)
- Gross-positive before costs: **202** (12.62%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -4.21 bps (min -40.61, max 10.88)**
- Expected net edge: **mean -40.16 bps (min -76.42, max -25.12)**
- Observed terminal edge: **mean -40.09 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.81, max 36.00)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 1131 × `GROSS_NON_POSITIVE`
- 202 × `MODELED_COSTS_ERASE_EDGE`
- 154 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 55 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 54 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 4 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `9d4d2d448005ea211380c2b5c68387088ff9baf55ba8f6e1a22cd49f5f21808e`
