# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `6c3002c5ec2bf1e0c8ea0cdaca7aa593f5f95525055e8431d89a8e7e4ef89a01`
- Replay SHA-256: `45358709d121e26380dea85ac6f2e6c0ec19df72ebd5dbc160d426d3d0501379`

## Cumulative funnel

- Captured terminal cycles: **1270**
- Complete evidence: **1268** (99.84%)
- Structural constraints pass: **1052** (82.83%)
- Gross-positive before costs: **175** (13.78%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -3.98 bps (min -35.06, max 8.52)**
- Expected net edge: **mean -39.93 bps (min -70.89, max -27.47)**
- Observed terminal edge: **mean -39.86 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.83, max 35.99)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 877 × `GROSS_NON_POSITIVE`
- 175 × `MODELED_COSTS_ERASE_EDGE`
- 128 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 48 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 40 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `696dc5d964356f273eb10f6f2df8e1201965e627ba678ba498c3df08a31e5632`
