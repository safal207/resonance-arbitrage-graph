# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `41e389604ac879b4bd9e8d0f9f202cae41b82148a86dc93f879e478760f2b2c2`
- Replay SHA-256: `b2bbc3bde4162772f43bbec9005f7f2918215b1ed537864ce8d7a59db7e531d3`

## Cumulative funnel

- Captured terminal cycles: **1990**
- Complete evidence: **1984** (99.70%)
- Structural constraints pass: **1650** (82.91%)
- Gross-positive before costs: **226** (11.36%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -4.27 bps (min -40.61, max 10.88)**
- Expected net edge: **mean -40.21 bps (min -76.42, max -25.12)**
- Observed terminal edge: **mean -40.15 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.81, max 36.00)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 1424 × `GROSS_NON_POSITIVE`
- 226 × `MODELED_COSTS_ERASE_EDGE`
- 191 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 72 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 71 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 6 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `4bbbbfe32d8fa5f9f3f2a18ac9d379aeaaefbc4f66d0c79b168cc46169c118cf`
