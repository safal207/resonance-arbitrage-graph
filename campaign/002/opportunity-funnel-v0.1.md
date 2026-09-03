# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `e38b1cac93d15a8bd46e230cd2899fb24fa47d1a43de360895ed67cad570b3a3`
- Replay SHA-256: `9cdc605471a849b6d6a244b49a9936b84a570bd7666d6fe3863809ef2efd3223`

## Cumulative funnel

- Captured terminal cycles: **370**
- Complete evidence: **368** (99.46%)
- Structural constraints pass: **325** (87.84%)
- Gross-positive before costs: **49** (13.24%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -4.04 bps (min -29.56, max 8.52)**
- Expected net edge: **mean -39.99 bps (min -65.41, max -27.47)**
- Observed terminal edge: **mean -40.00 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.85, max 35.99)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 276 × `GROSS_NON_POSITIVE`
- 49 × `MODELED_COSTS_ERASE_EDGE`
- 21 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 11 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 11 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `27e3dd15a8509c517e23bfe475c81d9d2eb51640bfd408277654009e1d8e47c0`
