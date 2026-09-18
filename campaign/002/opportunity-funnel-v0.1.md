# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `4f4483351d5430909011f502bd51d26183d4ab90ccc612410841f82679ed0303`
- Replay SHA-256: `2a03e8fe9e8bbfe7155f775c15d89d9e29741b1177f2bdd5ca3ab20aca0a5b87`

## Cumulative funnel

- Captured terminal cycles: **1320**
- Complete evidence: **1318** (99.85%)
- Structural constraints pass: **1098** (83.18%)
- Gross-positive before costs: **180** (13.64%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -4.02 bps (min -40.61, max 10.88)**
- Expected net edge: **mean -39.96 bps (min -76.42, max -25.12)**
- Observed terminal edge: **mean -39.89 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.81, max 36.00)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 918 × `GROSS_NON_POSITIVE`
- 180 × `MODELED_COSTS_ERASE_EDGE`
- 130 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 49 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 41 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `cd91223c2e55201548050a3524db1d6848e9b0f1c79c7a7b3c34b2959d635a50`
