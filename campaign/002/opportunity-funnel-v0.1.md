# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `286403d3d61891fc621fa71964b72f2b8172a4e500fedf84e8aac2d18037bcfb`
- Replay SHA-256: `c22b70cd2f5b91dee7a33963e190562e238e59bdeb6be23045d4f78d64d7e167`

## Cumulative funnel

- Captured terminal cycles: **150**
- Complete evidence: **150** (100.00%)
- Structural constraints pass: **134** (89.33%)
- Gross-positive before costs: **23** (15.33%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -4.23 bps (min -29.56, max 5.22)**
- Expected net edge: **mean -40.17 bps (min -65.41, max -30.75)**
- Observed terminal edge: **mean -40.31 bps (min -88.73, max -30.80)**
- Modeled cost drag: **mean 35.94 bps (min 35.85, max 35.98)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 111 × `GROSS_NON_POSITIVE`
- 23 × `MODELED_COSTS_ERASE_EDGE`
- 7 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 6 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 3 × `STRUCTURAL:CAPACITY_EXCEEDED:0`

Evidence SHA-256: `a9fd5e428a1a284e50dc02fadd8c5ff7de2d32ba94e337a2a6fddbf5f3702f94`
