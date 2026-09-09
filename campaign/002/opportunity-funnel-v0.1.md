# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `2386091edf9ce02b139ab77cad776028d5ac1fe0d6451b46c8763c46aae2dc76`
- Replay SHA-256: `7c2e70e1ec91dc39ac247ee30e8b76250c8d2cacc2c78b59ae13ce56dba410d9`

## Cumulative funnel

- Captured terminal cycles: **778**
- Complete evidence: **776** (99.74%)
- Structural constraints pass: **663** (85.22%)
- Gross-positive before costs: **117** (15.04%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -3.90 bps (min -35.06, max 8.52)**
- Expected net edge: **mean -39.84 bps (min -70.89, max -27.47)**
- Observed terminal edge: **mean -39.80 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.83, max 35.99)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 546 × `GROSS_NON_POSITIVE`
- 117 × `MODELED_COSTS_ERASE_EDGE`
- 63 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 26 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 24 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `9a1fcfb73c32505e1b71a2c91ecb6b97a457f728b632e953a6d988051bf89e06`
