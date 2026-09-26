# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `bbcb51bcebfea276b673529ce6b1b5ce1262b36abb34bf492ca51dd1b61f3ad8`
- Replay SHA-256: `16ed6123cebe762b2f5e904fcb0a87902ec5873236b97542d5c08ce668b8d648`

## Cumulative funnel

- Captured terminal cycles: **1820**
- Complete evidence: **1816** (99.78%)
- Structural constraints pass: **1508** (82.86%)
- Gross-positive before costs: **217** (11.92%)
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

- 1291 × `GROSS_NON_POSITIVE`
- 217 × `MODELED_COSTS_ERASE_EDGE`
- 177 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 66 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 65 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 4 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `6163326eb273a0c47c8b9a38c31cf35352f04426e39f0d35526d7990a7546ddb`
