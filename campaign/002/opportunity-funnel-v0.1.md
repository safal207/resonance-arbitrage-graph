# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `c73a22a05f621bdb87a649458cf0be4322104f148a79ec8fcbf0dd65fe9c375f`
- Replay SHA-256: `fb994c254469a3829191e337128dada86c1eaedad97bfb72ac51389ec665b245`

## Cumulative funnel

- Captured terminal cycles: **1970**
- Complete evidence: **1966** (99.80%)
- Structural constraints pass: **1632** (82.84%)
- Gross-positive before costs: **225** (11.42%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -4.28 bps (min -40.61, max 10.88)**
- Expected net edge: **mean -40.22 bps (min -76.42, max -25.12)**
- Observed terminal edge: **mean -40.15 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.81, max 36.00)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 1407 × `GROSS_NON_POSITIVE`
- 225 × `MODELED_COSTS_ERASE_EDGE`
- 191 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 72 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 71 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 4 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `7b0a9aecb95b0ae77eb4b3b4ae1f3dcc3218922a565d94f2d3f6ddd68df7c693`
