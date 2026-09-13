# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `229aaa1ce0a2c6fda38a14cee55e26b91291815d5473ad94430353f1a7f390ff`
- Replay SHA-256: `35628f344c5d92864eaed02ebcdb3e6892f74fb849be5266f099b153d784a1d5`

## Cumulative funnel

- Captured terminal cycles: **1040**
- Complete evidence: **1038** (99.81%)
- Structural constraints pass: **874** (84.04%)
- Gross-positive before costs: **153** (14.71%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -3.91 bps (min -35.06, max 8.52)**
- Expected net edge: **mean -39.86 bps (min -70.89, max -27.47)**
- Observed terminal edge: **mean -39.81 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.83, max 35.99)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 721 × `GROSS_NON_POSITIVE`
- 153 × `MODELED_COSTS_ERASE_EDGE`
- 102 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 33 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 29 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `504cf52eb54d7cc8942fdee496e2816c2aa7e0039e3b9fc519de0b1d81a1f730`
