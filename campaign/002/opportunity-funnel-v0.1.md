# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `244a26824c877fe9b6741fab87ac0b75082d66c1f1952499f79efa94f4e8a674`
- Replay SHA-256: `1d9243def4f10e03a86e2a2541c572f39921c3e26a42dd8e51326eba737ef4ca`

## Cumulative funnel

- Captured terminal cycles: **550**
- Complete evidence: **548** (99.64%)
- Structural constraints pass: **474** (86.18%)
- Gross-positive before costs: **81** (14.73%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -3.88 bps (min -35.06, max 8.52)**
- Expected net edge: **mean -39.83 bps (min -70.89, max -27.47)**
- Observed terminal edge: **mean -39.82 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.83, max 35.99)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 393 × `GROSS_NON_POSITIVE`
- 81 × `MODELED_COSTS_ERASE_EDGE`
- 37 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 19 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 18 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `6ed427cecd76561dcf822d10134534d09466ed8daaf08e3ffdce3b37dba9722d`
