# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `0103b3cc610b1e7254e77a63b855535be8b1ad73a2cb150ab3f1a9e5dfb3693a`
- Replay SHA-256: `f1847c96c283117029e23fadbc304def3c8ed72a047124465b740042ad09de1b`

## Cumulative funnel

- Captured terminal cycles: **520**
- Complete evidence: **518** (99.62%)
- Structural constraints pass: **450** (86.54%)
- Gross-positive before costs: **74** (14.23%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -3.93 bps (min -35.06, max 8.52)**
- Expected net edge: **mean -39.87 bps (min -70.89, max -27.47)**
- Observed terminal edge: **mean -39.86 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.83, max 35.99)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 376 × `GROSS_NON_POSITIVE`
- 74 × `MODELED_COSTS_ERASE_EDGE`
- 34 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 18 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 16 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `c1df9bbeba59632ab50673135e28bdf683e18b9e67809532e8763274e45f544d`
