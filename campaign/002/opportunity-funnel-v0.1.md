# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `859bca908179b85820745c120368e7ef83eae5ad13e99c0dde898e2cf7618e2b`
- Replay SHA-256: `4e7d0c6adbee1b25d1749fe9f00d73d126c248e001da0e247b4fac656ece422f`

## Cumulative funnel

- Captured terminal cycles: **140**
- Complete evidence: **140** (100.00%)
- Structural constraints pass: **127** (90.71%)
- Gross-positive before costs: **22** (15.71%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -4.22 bps (min -29.56, max 5.22)**
- Expected net edge: **mean -40.16 bps (min -65.41, max -30.75)**
- Observed terminal edge: **mean -40.34 bps (min -88.73, max -30.80)**
- Modeled cost drag: **mean 35.94 bps (min 35.85, max 35.98)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 105 × `GROSS_NON_POSITIVE`
- 22 × `MODELED_COSTS_ERASE_EDGE`
- 6 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 6 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 1 × `STRUCTURAL:CAPACITY_EXCEEDED:0`

Evidence SHA-256: `d1c292ed05c41d74d81942d2bb8c6325225171b8b16868d0ab07aa187ad39bbe`
