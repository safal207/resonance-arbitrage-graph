# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `feb2bec14e0610593cd4821675908e233278ff0f7e48a38fac99a0a182cd3375`
- Replay SHA-256: `1f6e2a0e573bd1d95a41b4390f6a5ada6b416c20b00ffdb9a1585eecf6eaa6ac`

## Cumulative funnel

- Captured terminal cycles: **1420**
- Complete evidence: **1418** (99.86%)
- Structural constraints pass: **1182** (83.24%)
- Gross-positive before costs: **186** (13.10%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -4.09 bps (min -40.61, max 10.88)**
- Expected net edge: **mean -40.03 bps (min -76.42, max -25.12)**
- Observed terminal edge: **mean -39.94 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.81, max 36.00)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 996 × `GROSS_NON_POSITIVE`
- 186 × `MODELED_COSTS_ERASE_EDGE`
- 136 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 53 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 47 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `cb720f059b0228db8d2b42e332f14fefa8dc3e9a9ab12488eeccbdaf8c2f4450`
