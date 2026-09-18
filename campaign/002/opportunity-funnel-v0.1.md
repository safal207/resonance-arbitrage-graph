# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `394fc5aea257f33500c90b3f06cc44779f4509170e18bed9197a2d6196f2f2c4`
- Replay SHA-256: `7d2bfc1c84e5ca54971faa50ae3c404b3bacf88ea1daeb8d4c59c2e016646fd5`

## Cumulative funnel

- Captured terminal cycles: **1370**
- Complete evidence: **1368** (99.85%)
- Structural constraints pass: **1134** (82.77%)
- Gross-positive before costs: **182** (13.28%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -4.09 bps (min -40.61, max 10.88)**
- Expected net edge: **mean -40.03 bps (min -76.42, max -25.12)**
- Observed terminal edge: **mean -39.95 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.81, max 36.00)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 952 × `GROSS_NON_POSITIVE`
- 182 × `MODELED_COSTS_ERASE_EDGE`
- 134 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 53 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 47 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `ff52369b69e83b2ed4e1aabe7d5e7649fa0dfeaa65e8688914c35c63371b285c`
