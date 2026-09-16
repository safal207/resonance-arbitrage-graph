# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `465a7abac058c40b086ef9423e5d2e13a2ad6ebf290593afd6014f7d27b5407a`
- Replay SHA-256: `2de2f5f90c61143bdb4d1807a33288dc2aa6c05f5ae63edf2fd558804be7b6dd`

## Cumulative funnel

- Captured terminal cycles: **1240**
- Complete evidence: **1238** (99.84%)
- Structural constraints pass: **1024** (82.58%)
- Gross-positive before costs: **172** (13.87%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -3.98 bps (min -35.06, max 8.52)**
- Expected net edge: **mean -39.93 bps (min -70.89, max -27.47)**
- Observed terminal edge: **mean -39.86 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.83, max 35.99)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 852 × `GROSS_NON_POSITIVE`
- 172 × `MODELED_COSTS_ERASE_EDGE`
- 128 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 47 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 39 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `8f3c8100ac5d942e7ca82c80727789ece2d09fab09468cf4731e18fb4a6eda34`
