# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `67d57e6f7f430b852a9070a4e02824ad1aaa6c5a67d906e69d01222fb80995d5`
- Replay SHA-256: `f917c839cf5b3e7346a2c7d902b53ce6578b52489e422d23accb4c0172a6ff88`

## Cumulative funnel

- Captured terminal cycles: **420**
- Complete evidence: **418** (99.52%)
- Structural constraints pass: **362** (86.19%)
- Gross-positive before costs: **53** (12.62%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -4.00 bps (min -29.56, max 8.52)**
- Expected net edge: **mean -39.95 bps (min -65.41, max -27.47)**
- Observed terminal edge: **mean -39.96 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.85, max 35.99)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 309 × `GROSS_NON_POSITIVE`
- 53 × `MODELED_COSTS_ERASE_EDGE`
- 29 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 14 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 13 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `39ca57b954053f69deec028a953ce70c71a7eeeaa3e9290e9f5bc16c01ec4853`
