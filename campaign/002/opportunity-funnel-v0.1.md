# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `50c7a405d78e002fe27dd49007cfe15a537942432a6954dbce822dfadb9db409`
- Replay SHA-256: `b86aa6bfbf4b1e7fe4b77241500737d0cb98c28660553b5941ba58e24e0cc13b`

## Cumulative funnel

- Captured terminal cycles: **490**
- Complete evidence: **488** (99.59%)
- Structural constraints pass: **423** (86.33%)
- Gross-positive before costs: **68** (13.88%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -3.89 bps (min -29.56, max 8.52)**
- Expected net edge: **mean -39.84 bps (min -65.41, max -27.47)**
- Observed terminal edge: **mean -39.88 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.85, max 35.99)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 355 × `GROSS_NON_POSITIVE`
- 68 × `MODELED_COSTS_ERASE_EDGE`
- 32 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 18 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 15 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `eeb0d9f8bc78689806457d250328ede14aad97e15ce194d0d8b49aacb49d76ba`
