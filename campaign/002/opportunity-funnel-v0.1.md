# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `3d88b6f856fc73f00719ed38083f3102809913e831c440b3e32c05dd74bf6cc2`
- Replay SHA-256: `afedc1f7c9aaea0f8c1989562a8cde2014cd1dceb5e2df70abfedde09011943c`

## Cumulative funnel

- Captured terminal cycles: **1450**
- Complete evidence: **1448** (99.86%)
- Structural constraints pass: **1208** (83.31%)
- Gross-positive before costs: **189** (13.03%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -4.10 bps (min -40.61, max 10.88)**
- Expected net edge: **mean -40.04 bps (min -76.42, max -25.12)**
- Observed terminal edge: **mean -39.96 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.81, max 36.00)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 1019 × `GROSS_NON_POSITIVE`
- 189 × `MODELED_COSTS_ERASE_EDGE`
- 139 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 53 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 48 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `397cf89ea2b3fe840c412922c8803b581be0bec32541c447b62bc639db17377e`
