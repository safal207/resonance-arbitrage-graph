# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `4bcf55c615e370820b4a6f8076fd89ef54a3fb6f33f63d29e86ce45431a2d992`
- Replay SHA-256: `c6dc1922fc1e2b6e4df0b04442f6cc9bc031e2eb063ab96279ba7630f57a7b98`

## Cumulative funnel

- Captured terminal cycles: **1930**
- Complete evidence: **1926** (99.79%)
- Structural constraints pass: **1597** (82.75%)
- Gross-positive before costs: **222** (11.50%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -4.26 bps (min -40.61, max 10.88)**
- Expected net edge: **mean -40.20 bps (min -76.42, max -25.12)**
- Observed terminal edge: **mean -40.12 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.81, max 36.00)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 1375 × `GROSS_NON_POSITIVE`
- 222 × `MODELED_COSTS_ERASE_EDGE`
- 190 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 71 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 68 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 4 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `dd08045c7ebfc08191cf6516f7291d18d32af3a08a7911e3ef27eddead8d2498`
