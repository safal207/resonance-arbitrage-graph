# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `be473c1b8b86ad67bd7a376b844f790ca73a0caf0f74a9008881e1570844c330`
- Replay SHA-256: `b5a020ef8bdfc298bc3bf3a1a5e90f50356120d2015736c00e7b1dfe233c0a7d`

## Cumulative funnel

- Captured terminal cycles: **290**
- Complete evidence: **290** (100.00%)
- Structural constraints pass: **256** (88.28%)
- Gross-positive before costs: **41** (14.14%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -4.14 bps (min -29.56, max 8.52)**
- Expected net edge: **mean -40.09 bps (min -65.41, max -27.47)**
- Observed terminal edge: **mean -40.06 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.85, max 35.99)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 215 × `GROSS_NON_POSITIVE`
- 41 × `MODELED_COSTS_ERASE_EDGE`
- 13 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 11 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 10 × `STRUCTURAL:CAPACITY_EXCEEDED:0`

Evidence SHA-256: `f494dfdd670b1660a26dfd89853ece6f42163c36f4e0c3f9e6ca6886873a030d`
