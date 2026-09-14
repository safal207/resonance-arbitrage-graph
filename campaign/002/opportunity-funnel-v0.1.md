# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `32c71a0ed3033be54044d1fdedff83dc396e226b5597a9347b3853901c967d74`
- Replay SHA-256: `40088d7b856d8a5badd6f7f9211ddb257c1ade0fa92b64caa21d759090bfe1cf`

## Cumulative funnel

- Captured terminal cycles: **1100**
- Complete evidence: **1098** (99.82%)
- Structural constraints pass: **921** (83.73%)
- Gross-positive before costs: **159** (14.45%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -3.93 bps (min -35.06, max 8.52)**
- Expected net edge: **mean -39.88 bps (min -70.89, max -27.47)**
- Observed terminal edge: **mean -39.82 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.83, max 35.99)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 762 × `GROSS_NON_POSITIVE`
- 159 × `MODELED_COSTS_ERASE_EDGE`
- 112 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 35 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 30 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `b94cb245bdd47f8d43a3bd054c3db3aabcd55ee03784dceced1dc2b75b150866`
