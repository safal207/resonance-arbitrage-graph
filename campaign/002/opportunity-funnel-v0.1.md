# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `6aaa9133a7ded7b77379e3d74f92b3d3f5a4a00fa5d9df6f2822448084f9eb84`
- Replay SHA-256: `3e78aa966d721b26cf85550e78ac4c00429df21b7fc91e6a4429eb2223e6b175`

## Cumulative funnel

- Captured terminal cycles: **1860**
- Complete evidence: **1856** (99.78%)
- Structural constraints pass: **1543** (82.96%)
- Gross-positive before costs: **218** (11.72%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -4.27 bps (min -40.61, max 10.88)**
- Expected net edge: **mean -40.21 bps (min -76.42, max -25.12)**
- Observed terminal edge: **mean -40.13 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.81, max 36.00)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 1325 × `GROSS_NON_POSITIVE`
- 218 × `MODELED_COSTS_ERASE_EDGE`
- 181 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 67 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 65 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 4 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `3325e65fcdb4e787b1bf3a24751b628700f72392e6089965e39ecd8a926de390`
