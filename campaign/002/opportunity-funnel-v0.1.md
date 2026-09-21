# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `6d4384dd541f01998d04ac7f07c5b4197f241e55f417946ff3bfea848e34214b`
- Replay SHA-256: `135ae80261bbea44f4610ebb73cf97df588848c89de21357cb62c4ab30530a99`

## Cumulative funnel

- Captured terminal cycles: **1540**
- Complete evidence: **1538** (99.87%)
- Structural constraints pass: **1284** (83.38%)
- Gross-positive before costs: **197** (12.79%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -4.20 bps (min -40.61, max 10.88)**
- Expected net edge: **mean -40.14 bps (min -76.42, max -25.12)**
- Observed terminal edge: **mean -40.04 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.81, max 36.00)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 1087 × `GROSS_NON_POSITIVE`
- 197 × `MODELED_COSTS_ERASE_EDGE`
- 149 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 55 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 50 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `a0422a0e037f4a1c52ff9300703e498f702325ff2f6c2ab62f0bfe49bf7667ca`
