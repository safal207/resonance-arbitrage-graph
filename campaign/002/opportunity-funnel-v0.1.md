# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `92f001ef97d40ec1edbeb87c5d6a71def4f9bb8d5e537f79ba592a87253c225d`
- Replay SHA-256: `7908b2f62021c250113cc6288ce19477a8e08fec48f95ca303d520e24a34d752`

## Cumulative funnel

- Captured terminal cycles: **1960**
- Complete evidence: **1956** (99.80%)
- Structural constraints pass: **1622** (82.76%)
- Gross-positive before costs: **224** (11.43%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -4.27 bps (min -40.61, max 10.88)**
- Expected net edge: **mean -40.21 bps (min -76.42, max -25.12)**
- Observed terminal edge: **mean -40.14 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.81, max 36.00)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 1398 × `GROSS_NON_POSITIVE`
- 224 × `MODELED_COSTS_ERASE_EDGE`
- 191 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 72 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 71 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 4 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `b49c9788ea1b941ec016cc641bc2bdbd70dec2ce2ea7cc352cb238c0ec814007`
