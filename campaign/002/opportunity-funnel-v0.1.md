# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `e0973abf38dc31b916ffa504e31c32c40b0f1a22cb37aeebcc0408a251bf32df`
- Replay SHA-256: `a8df1e50a9c90d4a38edf78eb1b284067a3a7fcb2263955240cd88b688ef4886`

## Cumulative funnel

- Captured terminal cycles: **190**
- Complete evidence: **190** (100.00%)
- Structural constraints pass: **171** (90.00%)
- Gross-positive before costs: **27** (14.21%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -4.20 bps (min -29.56, max 5.22)**
- Expected net edge: **mean -40.15 bps (min -65.41, max -30.75)**
- Observed terminal edge: **mean -40.22 bps (min -88.73, max -30.80)**
- Modeled cost drag: **mean 35.94 bps (min 35.85, max 35.98)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 144 × `GROSS_NON_POSITIVE`
- 27 × `MODELED_COSTS_ERASE_EDGE`
- 9 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 7 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 3 × `STRUCTURAL:CAPACITY_EXCEEDED:0`

Evidence SHA-256: `8af2fa01547a79d11963cda4e4583ac572294dbb753127abc996fb3dd1a4cd16`
