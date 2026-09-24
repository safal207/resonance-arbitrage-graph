# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `bec0bff01325579faeb64ba6f1cf0e6a4edff9e0f6e8d67f3b18d03488df86d5`
- Replay SHA-256: `bc1acc3302587fa3aaa1d2fc870efba65523fdaa1b8e51732c372b47a897cf5a`

## Cumulative funnel

- Captured terminal cycles: **1730**
- Complete evidence: **1726** (99.77%)
- Structural constraints pass: **1435** (82.95%)
- Gross-positive before costs: **210** (12.14%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -4.25 bps (min -40.61, max 10.88)**
- Expected net edge: **mean -40.19 bps (min -76.42, max -25.12)**
- Observed terminal edge: **mean -40.12 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.81, max 36.00)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 1225 × `GROSS_NON_POSITIVE`
- 210 × `MODELED_COSTS_ERASE_EDGE`
- 167 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 63 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 61 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 4 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `027dd66bf396faa822fb3f7efc48bba64962d2b83ec567c8a05960b32c958a13`
