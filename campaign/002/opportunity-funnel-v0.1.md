# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `cfb83eafe472354fa7f5e6fa39ad80af56d413ab81de6cd50100fb95dc57f92a`
- Replay SHA-256: `2e83a8a1f54a7bcadf1ded41a92c79c7056993e8dea9082249f9f667e80a4fa9`

## Cumulative funnel

- Captured terminal cycles: **1850**
- Complete evidence: **1846** (99.78%)
- Structural constraints pass: **1534** (82.92%)
- Gross-positive before costs: **218** (11.78%)
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

- 1316 × `GROSS_NON_POSITIVE`
- 218 × `MODELED_COSTS_ERASE_EDGE`
- 180 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 67 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 65 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 4 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `90e1ca677e17f76468db489173f1ee0ac1bff822ff870bae2bf43e1182bdc107`
