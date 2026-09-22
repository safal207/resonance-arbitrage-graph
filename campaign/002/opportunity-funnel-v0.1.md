# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `12934a33b6751c8821678bbf4204360c390dcc506ceed6945aa15cdc7e6243dd`
- Replay SHA-256: `25a87613497bdccd38dfd94b140677028af9ffac9ef052706098357b99867253`

## Cumulative funnel

- Captured terminal cycles: **1628**
- Complete evidence: **1624** (99.75%)
- Structural constraints pass: **1355** (83.23%)
- Gross-positive before costs: **203** (12.47%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -4.23 bps (min -40.61, max 10.88)**
- Expected net edge: **mean -40.18 bps (min -76.42, max -25.12)**
- Observed terminal edge: **mean -40.10 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.81, max 36.00)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 1152 × `GROSS_NON_POSITIVE`
- 203 × `MODELED_COSTS_ERASE_EDGE`
- 156 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 57 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 56 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 4 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `0c2b4776819dbd644e4f464fc519f18cad3e7c31769e7d100d0a8d24a4b99260`
