# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `1aba91f259c8af2e2c32c059e41171c2005ad118a97f2c065435c868a4343861`
- Replay SHA-256: `9e4b228b1aa48b1b3e26753c3a77a8dafb3b9162c82e3e5745f3e088c5129ba7`

## Cumulative funnel

- Captured terminal cycles: **1190**
- Complete evidence: **1188** (99.83%)
- Structural constraints pass: **985** (82.77%)
- Gross-positive before costs: **169** (14.20%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -3.94 bps (min -35.06, max 8.52)**
- Expected net edge: **mean -39.88 bps (min -70.89, max -27.47)**
- Observed terminal edge: **mean -39.83 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.83, max 35.99)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 816 × `GROSS_NON_POSITIVE`
- 169 × `MODELED_COSTS_ERASE_EDGE`
- 122 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 42 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 39 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `448c94f607019b1aae83ba39faa7d88bdef8953f09021db83d3389cf70f46b88`
