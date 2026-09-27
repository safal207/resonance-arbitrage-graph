# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `dd87ac17ff002bfc31715098b8d62cbaf47d5067ee2f78ff1b837976ebd0b45b`
- Replay SHA-256: `6721b5e49d8d3bb9085a6f1ddb39d56a9dc4735f9d3c5525aa11e44288c567b5`

## Cumulative funnel

- Captured terminal cycles: **1890**
- Complete evidence: **1886** (99.79%)
- Structural constraints pass: **1565** (82.80%)
- Gross-positive before costs: **221** (11.69%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -4.26 bps (min -40.61, max 10.88)**
- Expected net edge: **mean -40.20 bps (min -76.42, max -25.12)**
- Observed terminal edge: **mean -40.13 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.81, max 36.00)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 1344 × `GROSS_NON_POSITIVE`
- 221 × `MODELED_COSTS_ERASE_EDGE`
- 186 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 69 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 66 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 4 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `c0d81d40372ab1d931261ae419ed7ea2b483a99159ba3c43f2b447f4171fd813`
