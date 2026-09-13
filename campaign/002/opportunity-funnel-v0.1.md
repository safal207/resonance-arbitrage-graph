# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `66788474313d5e28da0bcd23d2f9aaa5cb75ee5ac2f06821864596b600b351da`
- Replay SHA-256: `378dd00efa1306a93ef917aa676e511a03fa0ab434d63699f0a2cd6c614b52f7`

## Cumulative funnel

- Captured terminal cycles: **1070**
- Complete evidence: **1068** (99.81%)
- Structural constraints pass: **898** (83.93%)
- Gross-positive before costs: **157** (14.67%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -3.91 bps (min -35.06, max 8.52)**
- Expected net edge: **mean -39.85 bps (min -70.89, max -27.47)**
- Observed terminal edge: **mean -39.80 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.83, max 35.99)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 741 × `GROSS_NON_POSITIVE`
- 157 × `MODELED_COSTS_ERASE_EDGE`
- 107 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 34 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 29 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `5363234e92ddc6765193d189ee4867dc9fe0930e8f9e1f6ff22614d2f32c55fa`
