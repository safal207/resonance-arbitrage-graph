# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `a4d5714fefa75402e2a24d0e00ddd21fd49308adc9f0c0e19453bfa8f2d6b086`
- Replay SHA-256: `54081a4d76c1c8ccba0f22be3d972fb0ff408ae8193b82f38a91301211bdadb0`

## Cumulative funnel

- Captured terminal cycles: **1500**
- Complete evidence: **1498** (99.87%)
- Structural constraints pass: **1246** (83.07%)
- Gross-positive before costs: **192** (12.80%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -4.18 bps (min -40.61, max 10.88)**
- Expected net edge: **mean -40.12 bps (min -76.42, max -25.12)**
- Observed terminal edge: **mean -40.03 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.81, max 36.00)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 1054 × `GROSS_NON_POSITIVE`
- 192 × `MODELED_COSTS_ERASE_EDGE`
- 148 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 54 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 50 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `8bb6ae77409c5ad626255308bb7d75533f08fbd9dfcdf20e19e7c7eb25bcb4ed`
