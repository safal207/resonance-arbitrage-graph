# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `75f17496cbff5d9ac5e74f14b366051174e9cd6bd8b9bbb5ca20e3f922f389c5`
- Replay SHA-256: `98c8b867c34d55749797f648bff8230c127ccecdaaffa4efab913fe5e8b918b5`

## Cumulative funnel

- Captured terminal cycles: **230**
- Complete evidence: **230** (100.00%)
- Structural constraints pass: **202** (87.83%)
- Gross-positive before costs: **33** (14.35%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -4.25 bps (min -29.56, max 5.22)**
- Expected net edge: **mean -40.19 bps (min -65.41, max -30.75)**
- Observed terminal edge: **mean -40.18 bps (min -88.73, max -30.80)**
- Modeled cost drag: **mean 35.94 bps (min 35.85, max 35.98)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 169 × `GROSS_NON_POSITIVE`
- 33 × `MODELED_COSTS_ERASE_EDGE`
- 11 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 9 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 8 × `STRUCTURAL:CAPACITY_EXCEEDED:0`

Evidence SHA-256: `5ccb250f3999523f3b84ac025e7a442d88ea70f0061b54f5eb5f173c8f4f1830`
