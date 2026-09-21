# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `6f2e3f7f1cde76a2453875f105b32195e556e30bc324ad8510f5371842705767`
- Replay SHA-256: `a21628f3b3be288549fff45a0e239d0c2888bed4215583e6bc3c66e8b14f93bf`

## Cumulative funnel

- Captured terminal cycles: **1560**
- Complete evidence: **1558** (99.87%)
- Structural constraints pass: **1301** (83.40%)
- Gross-positive before costs: **200** (12.82%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -4.20 bps (min -40.61, max 10.88)**
- Expected net edge: **mean -40.14 bps (min -76.42, max -25.12)**
- Observed terminal edge: **mean -40.06 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.81, max 36.00)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 1101 × `GROSS_NON_POSITIVE`
- 200 × `MODELED_COSTS_ERASE_EDGE`
- 150 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 55 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 52 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `be91b1ac1b7cd26fd263fba647263f8fabc147581996e07e9ac906927498af35`
