# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `a95470578b99e047c3046c4f75506418811b8c013d410d613c7b140b52543410`
- Replay SHA-256: `20656b2783de8e5e31e3fb1481b2d98408cdfd275a28a708582dd8153bc73fff`

## Cumulative funnel

- Captured terminal cycles: **848**
- Complete evidence: **846** (99.76%)
- Structural constraints pass: **717** (84.55%)
- Gross-positive before costs: **124** (14.62%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -3.92 bps (min -35.06, max 8.52)**
- Expected net edge: **mean -39.86 bps (min -70.89, max -27.47)**
- Observed terminal edge: **mean -39.82 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.83, max 35.99)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 593 × `GROSS_NON_POSITIVE`
- 124 × `MODELED_COSTS_ERASE_EDGE`
- 78 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 27 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 24 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `d42924e98d6abe81b6e19006ea115ded2e49263daaacfe18c61564262f654f3b`
