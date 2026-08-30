# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `5564f2e7b5422a2b6aaef3714befc02002b00504d0c65ae53a776b7fd96444d8`
- Replay SHA-256: `9f45ca28ba4de53d451588331acefe65139a9569e0206f3c1b58ed7c64a24849`

## Cumulative funnel

- Captured terminal cycles: **120**
- Complete evidence: **120** (100.00%)
- Structural constraints pass: **108** (90.00%)
- Gross-positive before costs: **20** (16.67%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -4.03 bps (min -29.56, max 5.22)**
- Expected net edge: **mean -39.97 bps (min -65.41, max -30.75)**
- Observed terminal edge: **mean -40.25 bps (min -88.73, max -30.80)**
- Modeled cost drag: **mean 35.94 bps (min 35.85, max 35.98)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 88 × `GROSS_NON_POSITIVE`
- 20 × `MODELED_COSTS_ERASE_EDGE`
- 6 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 5 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 1 × `STRUCTURAL:CAPACITY_EXCEEDED:0`

Evidence SHA-256: `b7e15500a6c106185c214ae0b398cd5088a6ea12cac4bf2ec7f385e7c62e5337`
