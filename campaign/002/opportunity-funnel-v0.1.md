# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `8e905b2f29b6ee1ec0603e5583bd7d1112bf4fb0c2ebdcfda511ab1743fa4667`
- Replay SHA-256: `e4f1626ea312bbe6ecb2b77ca38ad07a1114ddf15bb098f79bb7f6a3a67ff740`

## Cumulative funnel

- Captured terminal cycles: **1610**
- Complete evidence: **1606** (99.75%)
- Structural constraints pass: **1340** (83.23%)
- Gross-positive before costs: **203** (12.61%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -4.22 bps (min -40.61, max 10.88)**
- Expected net edge: **mean -40.16 bps (min -76.42, max -25.12)**
- Observed terminal edge: **mean -40.09 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.81, max 36.00)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 1137 × `GROSS_NON_POSITIVE`
- 203 × `MODELED_COSTS_ERASE_EDGE`
- 155 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 56 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 55 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 4 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `588ce6dda0f54c65b1e65c4c6e66ab8542bf5b95d5d35e29542c71cc00290a93`
