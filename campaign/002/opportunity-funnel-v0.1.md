# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `616ce646cb06394b6f2d8c084746e404a4558ffa6fb592317c24e24863c259f7`
- Replay SHA-256: `8d5656181a11b5dbed9599be77274f4c141a3977d416528ce7d5895b2f40c247`

## Cumulative funnel

- Captured terminal cycles: **280**
- Complete evidence: **280** (100.00%)
- Structural constraints pass: **248** (88.57%)
- Gross-positive before costs: **39** (13.93%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -4.17 bps (min -29.56, max 5.22)**
- Expected net edge: **mean -40.11 bps (min -65.41, max -30.75)**
- Observed terminal edge: **mean -40.08 bps (min -88.73, max -30.64)**
- Modeled cost drag: **mean 35.94 bps (min 35.85, max 35.98)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 209 × `GROSS_NON_POSITIVE`
- 39 × `MODELED_COSTS_ERASE_EDGE`
- 13 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 10 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 9 × `STRUCTURAL:CAPACITY_EXCEEDED:2`

Evidence SHA-256: `0015bab9814478546b0d54d66dfc1f0c89f8789a54d5e52fc90690c33aa3c528`
