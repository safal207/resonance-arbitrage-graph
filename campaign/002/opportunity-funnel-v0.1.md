# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `cc4da3eedad01dfd768ad2b5cf9696a84aae92822af81c7d27a3b9a2b6b66ccf`
- Replay SHA-256: `a18f7d0e3350cc4e1e4e8532825ff9e869c889c3e96bfe284621ba6b84a6b9b3`

## Cumulative funnel

- Captured terminal cycles: **450**
- Complete evidence: **448** (99.56%)
- Structural constraints pass: **390** (86.67%)
- Gross-positive before costs: **60** (13.33%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -3.96 bps (min -29.56, max 8.52)**
- Expected net edge: **mean -39.90 bps (min -65.41, max -27.47)**
- Observed terminal edge: **mean -39.90 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.85, max 35.99)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 330 × `GROSS_NON_POSITIVE`
- 60 × `MODELED_COSTS_ERASE_EDGE`
- 29 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 16 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 13 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `b2588d38b5bd5d831b98f402c32d8e67d67b2d63fe6a21e070bd346c65ffd037`
