# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `634aa3fc9d87e80099c9131f3d89c22751ddc750e13e10584ce3ea38e5d85592`
- Replay SHA-256: `d240a5413f4e12ddec01a5217fe7c987659ec49b5106c7daa3ddd327f1884450`

## Cumulative funnel

- Captured terminal cycles: **798**
- Complete evidence: **796** (99.75%)
- Structural constraints pass: **679** (85.09%)
- Gross-positive before costs: **120** (15.04%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -3.90 bps (min -35.06, max 8.52)**
- Expected net edge: **mean -39.84 bps (min -70.89, max -27.47)**
- Observed terminal edge: **mean -39.81 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.83, max 35.99)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 559 × `GROSS_NON_POSITIVE`
- 120 × `MODELED_COSTS_ERASE_EDGE`
- 67 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 26 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 24 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `b9f27b0bb7cef190fb137a589d681c105871d58716f69d781c68d62c0fac3b5c`
