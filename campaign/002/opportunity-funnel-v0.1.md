# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `8d7094e94cb48d402bc1ccb088aa9706daccf26a289f7afc7f136b627d0e13ba`
- Replay SHA-256: `18ec323ecd5e75b6fc8eda00298a5816225937b9d8ba9ae64e53751cb4541897`

## Cumulative funnel

- Captured terminal cycles: **100**
- Complete evidence: **100** (100.00%)
- Structural constraints pass: **90** (90.00%)
- Gross-positive before costs: **16** (16.00%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -4.04 bps (min -29.56, max 5.22)**
- Expected net edge: **mean -39.98 bps (min -65.41, max -30.75)**
- Observed terminal edge: **mean -40.32 bps (min -88.73, max -30.80)**
- Modeled cost drag: **mean 35.94 bps (min 35.85, max 35.98)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 74 × `GROSS_NON_POSITIVE`
- 16 × `MODELED_COSTS_ERASE_EDGE`
- 5 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 4 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 1 × `STRUCTURAL:CAPACITY_EXCEEDED:0`

Evidence SHA-256: `173fd3709a829b1ae6cc5df6851c5b80fc5461e8132298f4992863c6287d2a99`
