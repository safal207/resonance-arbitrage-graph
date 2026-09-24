# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `7b52b60c3bcdcdfb3ccde7f867a20712623bd459f2e23f7255b132df3d2d06af`
- Replay SHA-256: `91854c9c81e50fdcdb32cfe0d6c324c902299e9a8805a7d82c03f39fae02b18b`

## Cumulative funnel

- Captured terminal cycles: **1720**
- Complete evidence: **1716** (99.77%)
- Structural constraints pass: **1427** (82.97%)
- Gross-positive before costs: **210** (12.21%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -4.25 bps (min -40.61, max 10.88)**
- Expected net edge: **mean -40.19 bps (min -76.42, max -25.12)**
- Observed terminal edge: **mean -40.11 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.81, max 36.00)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 1217 × `GROSS_NON_POSITIVE`
- 210 × `MODELED_COSTS_ERASE_EDGE`
- 165 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 63 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 61 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 4 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `aded04fe4cc9955a3150d1ea50c77a5f00015a88101283ab04b917121dcf9672`
