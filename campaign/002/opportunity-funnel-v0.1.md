# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `b7db553e911b5ce825b4de99380a5d8686e2656665a0609fa9a265749c645554`
- Replay SHA-256: `0c540d74d3f3c4231c0d5df37b0845cb06cdcdb72643496a0f69f05d89f81e12`

## Cumulative funnel

- Captured terminal cycles: **1780**
- Complete evidence: **1776** (99.78%)
- Structural constraints pass: **1477** (82.98%)
- Gross-positive before costs: **214** (12.02%)
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

- 1263 × `GROSS_NON_POSITIVE`
- 214 × `MODELED_COSTS_ERASE_EDGE`
- 173 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 64 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 62 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 4 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `df7ae69440b891d9c8b8d824ff22fc2d4af1780125df0cc4adf3f1195e813b9b`
