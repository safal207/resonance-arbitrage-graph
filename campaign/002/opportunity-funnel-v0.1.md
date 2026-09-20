# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `79ff5da25b37c6caf7b77c7c74ab937b8b739fb2f0a522a7f060b3bed2d7aa94`
- Replay SHA-256: `a16b977fa1b506cc151ec44f291d528d00e6202599b1d72e42bc2ef3d0ef2c99`

## Cumulative funnel

- Captured terminal cycles: **1490**
- Complete evidence: **1488** (99.87%)
- Structural constraints pass: **1238** (83.09%)
- Gross-positive before costs: **189** (12.68%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -4.13 bps (min -40.61, max 10.88)**
- Expected net edge: **mean -40.07 bps (min -76.42, max -25.12)**
- Observed terminal edge: **mean -40.00 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.81, max 36.00)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 1049 × `GROSS_NON_POSITIVE`
- 189 × `MODELED_COSTS_ERASE_EDGE`
- 146 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 54 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 50 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `1ed1919f49399b0157d882cc2b3b586fa532f536aa8dfefac4141f6b66918469`
