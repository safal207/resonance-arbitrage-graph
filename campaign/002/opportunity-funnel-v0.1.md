# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `7e0b2ffe7a01829549265920f0e1b565116327a1476fb65163de4f4c8b3e43dd`
- Replay SHA-256: `ee4b9154e5758b2dc201e2737b692da73d591357cf850e57a54ea507d5d4f9c4`

## Cumulative funnel

- Captured terminal cycles: **580**
- Complete evidence: **578** (99.66%)
- Structural constraints pass: **500** (86.21%)
- Gross-positive before costs: **85** (14.66%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -3.88 bps (min -35.06, max 8.52)**
- Expected net edge: **mean -39.82 bps (min -70.89, max -27.47)**
- Observed terminal edge: **mean -39.81 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.83, max 35.99)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 415 × `GROSS_NON_POSITIVE`
- 85 × `MODELED_COSTS_ERASE_EDGE`
- 41 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 19 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 18 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `73fe66a9ae8b5be015aa804ffafc81e16b98318ef5c173043fb37a6928f8344b`
