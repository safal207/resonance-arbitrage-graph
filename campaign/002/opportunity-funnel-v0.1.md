# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `293ea97da104b9765b2665a4e4ec81d9b2624e61f6d50b689b20fe4179940816`
- Replay SHA-256: `ccb99013481c022f3d0ca2e84fd3e0a362f5d250f7bc7ae190b03840f2f1a86c`

## Cumulative funnel

- Captured terminal cycles: **1400**
- Complete evidence: **1398** (99.86%)
- Structural constraints pass: **1163** (83.07%)
- Gross-positive before costs: **184** (13.14%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -4.09 bps (min -40.61, max 10.88)**
- Expected net edge: **mean -40.03 bps (min -76.42, max -25.12)**
- Observed terminal edge: **mean -39.94 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.81, max 36.00)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 979 × `GROSS_NON_POSITIVE`
- 184 × `MODELED_COSTS_ERASE_EDGE`
- 135 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 53 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 47 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `e1c3e23914fd4a1e0e2deb66a8ba8d8ed7d33b3b6c1c68952de55c6ea6145afd`
