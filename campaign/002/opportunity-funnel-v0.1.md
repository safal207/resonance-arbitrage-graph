# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `bc3b51918955253bf24566a1a283ff98b155039991ab947c2b46b6a4f8226659`
- Replay SHA-256: `b88d6e404edcc7e83d813a66d68cd60bc06dd7f4f8e9f37c89d28aa8926ea378`

## Cumulative funnel

- Captured terminal cycles: **1280**
- Complete evidence: **1278** (99.84%)
- Structural constraints pass: **1062** (82.97%)
- Gross-positive before costs: **177** (13.83%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -3.99 bps (min -35.06, max 8.52)**
- Expected net edge: **mean -39.93 bps (min -70.89, max -27.47)**
- Observed terminal edge: **mean -39.86 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.83, max 35.99)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 885 × `GROSS_NON_POSITIVE`
- 177 × `MODELED_COSTS_ERASE_EDGE`
- 128 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 48 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 40 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `45c0a3a3cc579ccb3be099dcdc8c6e32430a776cf30b05221b346fb2e53e8511`
