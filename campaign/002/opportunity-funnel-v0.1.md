# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `a3d67a320c00fab0734083e180affaa18f73de37323698514048c9518867abb0`
- Replay SHA-256: `8641e4bc2cc77e8dbb5c3ef7365cbe457af4b496f07cc5e8063a3a03bfcd7485`

## Cumulative funnel

- Captured terminal cycles: **110**
- Complete evidence: **110** (100.00%)
- Structural constraints pass: **99** (90.00%)
- Gross-positive before costs: **18** (16.36%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -4.04 bps (min -29.56, max 5.22)**
- Expected net edge: **mean -39.98 bps (min -65.41, max -30.75)**
- Observed terminal edge: **mean -40.27 bps (min -88.73, max -30.80)**
- Modeled cost drag: **mean 35.94 bps (min 35.85, max 35.98)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 81 × `GROSS_NON_POSITIVE`
- 18 × `MODELED_COSTS_ERASE_EDGE`
- 6 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 4 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 1 × `STRUCTURAL:CAPACITY_EXCEEDED:0`

Evidence SHA-256: `0add4f8ee4984e74c8f20441153f18fe55b317fcd8a9ab22e040f50f494327f4`
