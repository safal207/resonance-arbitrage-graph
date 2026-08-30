# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `2a80c4053a310c1ea41755e0091330bd9480342a274f41de83255a4e9af3dac2`
- Replay SHA-256: `61255462bc3d2a22ca49bcb000c2e951497a4970cdd768328321f3decb0dac4e`

## Cumulative funnel

- Captured terminal cycles: **130**
- Complete evidence: **130** (100.00%)
- Structural constraints pass: **117** (90.00%)
- Gross-positive before costs: **21** (16.15%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -4.07 bps (min -29.56, max 5.22)**
- Expected net edge: **mean -40.01 bps (min -65.41, max -30.75)**
- Observed terminal edge: **mean -40.27 bps (min -88.73, max -30.80)**
- Modeled cost drag: **mean 35.94 bps (min 35.85, max 35.98)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 96 × `GROSS_NON_POSITIVE`
- 21 × `MODELED_COSTS_ERASE_EDGE`
- 6 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 6 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 1 × `STRUCTURAL:CAPACITY_EXCEEDED:0`

Evidence SHA-256: `a46662ffef18acf5cd42dd107cf92a6a3ddfd59c2275fbbed94261d49775cef7`
