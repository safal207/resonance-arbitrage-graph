# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `e7237e1c3e1071acfaa29ae640bb849b9fd02fbd50d61e9e1f271f026d7fa1c5`
- Replay SHA-256: `4432573337fbd4833d303ec4d1525af0c62942537e58541369ffa9adb66ff408`

## Cumulative funnel

- Captured terminal cycles: **300**
- Complete evidence: **300** (100.00%)
- Structural constraints pass: **264** (88.00%)
- Gross-positive before costs: **41** (13.67%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -4.12 bps (min -29.56, max 8.52)**
- Expected net edge: **mean -40.06 bps (min -65.41, max -27.47)**
- Observed terminal edge: **mean -40.04 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.85, max 35.99)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 223 × `GROSS_NON_POSITIVE`
- 41 × `MODELED_COSTS_ERASE_EDGE`
- 15 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 11 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 10 × `STRUCTURAL:CAPACITY_EXCEEDED:0`

Evidence SHA-256: `35fbcfb5bc3dedd34a329c97d67bf2674000114326dd805ca346a40cea027689`
