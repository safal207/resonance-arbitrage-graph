# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `39b4d4ad412b196ef8c3b5bdb446e93ce7f57afd3d29214351f91069bda7c087`
- Replay SHA-256: `ce613620fe86375b6b769047950d80387d6fc518e7a241ef3b8aa39dfc9e82f2`

## Cumulative funnel

- Captured terminal cycles: **60**
- Complete evidence: **60** (100.00%)
- Structural constraints pass: **55** (91.67%)
- Gross-positive before costs: **9** (15.00%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -4.08 bps (min -19.95, max 5.22)**
- Expected net edge: **mean -40.02 bps (min -55.84, max -30.75)**
- Observed terminal edge: **mean -39.99 bps (min -57.05, max -30.80)**
- Modeled cost drag: **mean 35.94 bps (min 35.89, max 35.98)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 46 × `GROSS_NON_POSITIVE`
- 9 × `MODELED_COSTS_ERASE_EDGE`
- 3 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 2 × `STRUCTURAL:CAPACITY_EXCEEDED:2`

Evidence SHA-256: `7bc1f79250d74c2c6367430f33320407e313f213ed7bb984aa9f500ed524fa15`
