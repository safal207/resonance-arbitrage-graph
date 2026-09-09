# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `b4701410085589d66e6b0614f185cfe6c1cf1025543468a41924e172414972e1`
- Replay SHA-256: `d759590cfa677fb4263c9ce89f45678bd57c3bcdf3ff770e169409c9f52beabd`

## Cumulative funnel

- Captured terminal cycles: **738**
- Complete evidence: **736** (99.73%)
- Structural constraints pass: **631** (85.50%)
- Gross-positive before costs: **111** (15.04%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -3.89 bps (min -35.06, max 8.52)**
- Expected net edge: **mean -39.83 bps (min -70.89, max -27.47)**
- Observed terminal edge: **mean -39.79 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.83, max 35.99)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 520 × `GROSS_NON_POSITIVE`
- 111 × `MODELED_COSTS_ERASE_EDGE`
- 58 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 24 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 23 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `ad52ecb6d3afaa21177ac140c9fc3ceeff9b00678526b98050640d4eba870bd5`
