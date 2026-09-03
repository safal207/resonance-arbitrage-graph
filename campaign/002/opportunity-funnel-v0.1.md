# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `75071357455453e5210b5cd1bee1bac958f2f8ac782a23e543dc5a864b24431d`
- Replay SHA-256: `d975bcb544c0f764baf0f1116171298d05cf1998cb8b7694b51f680fff278e9c`

## Cumulative funnel

- Captured terminal cycles: **320**
- Complete evidence: **318** (99.38%)
- Structural constraints pass: **282** (88.12%)
- Gross-positive before costs: **43** (13.44%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -4.06 bps (min -29.56, max 8.52)**
- Expected net edge: **mean -40.00 bps (min -65.41, max -27.47)**
- Observed terminal edge: **mean -40.00 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.85, max 35.99)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 239 × `GROSS_NON_POSITIVE`
- 43 × `MODELED_COSTS_ERASE_EDGE`
- 15 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 11 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 10 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `f2a060ac8bfcb7b756f955d94caf9d2d9dc3bb079e992094e3bd0f3abf2ab853`
