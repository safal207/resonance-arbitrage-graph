# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `4d522d40bde1c98caf13849f5b03a0e2da9a63341e8198d9b04d7f2194172287`
- Replay SHA-256: `59d0085ee90452ed56a28ec2f98e7be3a0a6b39ac0f056eb4cdc759194054fe5`

## Cumulative funnel

- Captured terminal cycles: **1920**
- Complete evidence: **1916** (99.79%)
- Structural constraints pass: **1591** (82.86%)
- Gross-positive before costs: **222** (11.56%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -4.26 bps (min -40.61, max 10.88)**
- Expected net edge: **mean -40.20 bps (min -76.42, max -25.12)**
- Observed terminal edge: **mean -40.12 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.81, max 36.00)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 1369 × `GROSS_NON_POSITIVE`
- 222 × `MODELED_COSTS_ERASE_EDGE`
- 189 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 69 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 67 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 4 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `e8898ea8a8384c21f5b73c90a005c2418da84e206f6e17b09a77e8146bbd8d05`
