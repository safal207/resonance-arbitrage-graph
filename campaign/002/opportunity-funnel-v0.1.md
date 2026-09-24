# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `541281235214dd37b9c0a245237abf44b52bbf5e58ebe903681f4b0164181df2`
- Replay SHA-256: `0d77fa95c00fb5e2bc47f06610aaf605f48246dc3039be502a912b465e05b890`

## Cumulative funnel

- Captured terminal cycles: **1760**
- Complete evidence: **1756** (99.77%)
- Structural constraints pass: **1460** (82.95%)
- Gross-positive before costs: **212** (12.05%)
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

- 1248 × `GROSS_NON_POSITIVE`
- 212 × `MODELED_COSTS_ERASE_EDGE`
- 170 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 64 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 62 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 4 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `e9cfdd9632fd386062109cc188aee2510e1553547914cdb11215e571ffde27d8`
