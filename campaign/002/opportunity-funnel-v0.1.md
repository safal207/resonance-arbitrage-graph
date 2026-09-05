# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `8cbcc2cdbeeee0674f2bc1b31e66d372c84a7d9a1cfea570f1bcf7e04630fe9c`
- Replay SHA-256: `a936f7d3c91fc395b60e87d1e73220e63193e69ae7f1ca625e3f667696670a5a`

## Cumulative funnel

- Captured terminal cycles: **510**
- Complete evidence: **508** (99.61%)
- Structural constraints pass: **441** (86.47%)
- Gross-positive before costs: **73** (14.31%)
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

- 368 × `GROSS_NON_POSITIVE`
- 73 × `MODELED_COSTS_ERASE_EDGE`
- 33 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 18 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 16 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `8a3912780ade29be56e90deffa8b0d6465aaf13919178a574813a41b6ac6fdfc`
