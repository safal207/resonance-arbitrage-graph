# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `510db47ea3ae318f3e7fd28788d4848ad1130014197547b6ada66290386e22a2`
- Replay SHA-256: `cfc2b5dfd32ad92a1d481ee9f6f95847f8cedab7a2b26da7e7bcdedd2e706d48`

## Cumulative funnel

- Captured terminal cycles: **1580**
- Complete evidence: **1576** (99.75%)
- Structural constraints pass: **1314** (83.16%)
- Gross-positive before costs: **201** (12.72%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -4.19 bps (min -40.61, max 10.88)**
- Expected net edge: **mean -40.14 bps (min -76.42, max -25.12)**
- Observed terminal edge: **mean -40.08 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.81, max 36.00)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 1113 × `GROSS_NON_POSITIVE`
- 201 × `MODELED_COSTS_ERASE_EDGE`
- 153 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 55 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 54 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 4 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `2c17009bc0fb0478cf260d002113177b89531acda8cbb1d4b52bda64c6c236a7`
