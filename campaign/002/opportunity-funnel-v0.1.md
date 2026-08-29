# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `81e61373d54d059e6c49a5e8c2884e6d821a710177e02f77e047c09b32393baa`
- Replay SHA-256: `940cc053747727b7d517176f21cd277c6faa3c04e49a1b812be96b5f7c1d9643`

## Cumulative funnel

- Captured terminal cycles: **30**
- Complete evidence: **30** (100.00%)
- Structural constraints pass: **28** (93.33%)
- Gross-positive before costs: **4** (13.33%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -4.23 bps (min -16.87, max 2.30)**
- Expected net edge: **mean -40.17 bps (min -52.77, max -33.66)**
- Observed terminal edge: **mean -40.04 bps (min -52.77, max -30.80)**
- Modeled cost drag: **mean 35.94 bps (min 35.90, max 35.97)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 24 × `GROSS_NON_POSITIVE`
- 4 × `MODELED_COSTS_ERASE_EDGE`
- 1 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 1 × `STRUCTURAL:CAPACITY_EXCEEDED:2`

Evidence SHA-256: `179b5da3472db330e520bfef768009862402ca7da7a23d4a28ca96f1234c54c3`
