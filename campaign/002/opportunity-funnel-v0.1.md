# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `fddcb43707e4501a7a6a9b02a71866aa0eb423a269054cdf0a7ef7ae058a9b83`
- Replay SHA-256: `9ac45fb9e6bb3ee41f7de0a6c836b078d1f234a99c36cf3d23ec76e9147e8d82`

## Cumulative funnel

- Captured terminal cycles: **1620**
- Complete evidence: **1616** (99.75%)
- Structural constraints pass: **1350** (83.33%)
- Gross-positive before costs: **203** (12.53%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -4.23 bps (min -40.61, max 10.88)**
- Expected net edge: **mean -40.17 bps (min -76.42, max -25.12)**
- Observed terminal edge: **mean -40.09 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.81, max 36.00)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 1147 × `GROSS_NON_POSITIVE`
- 203 × `MODELED_COSTS_ERASE_EDGE`
- 155 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 56 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 55 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 4 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `d703b0a240643553cc68ec4987b0a1a20b19ad4e31cdb7809803e114c732bb1c`
