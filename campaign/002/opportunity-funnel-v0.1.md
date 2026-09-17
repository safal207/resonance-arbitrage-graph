# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `5131ec35b50adc7cfbfb0a7006015771ac43abc6249b87eabe9c98fe598f58aa`
- Replay SHA-256: `c6d0505e5de10dbd01fb633948272624df3d6afea27a29b503fa3ab79096694b`

## Cumulative funnel

- Captured terminal cycles: **1260**
- Complete evidence: **1258** (99.84%)
- Structural constraints pass: **1043** (82.78%)
- Gross-positive before costs: **173** (13.73%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -3.99 bps (min -35.06, max 8.52)**
- Expected net edge: **mean -39.93 bps (min -70.89, max -27.47)**
- Observed terminal edge: **mean -39.86 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.83, max 35.99)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 870 × `GROSS_NON_POSITIVE`
- 173 × `MODELED_COSTS_ERASE_EDGE`
- 128 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 48 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 39 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `28e3ab4c91b0652fe17d30731023ea2da5a522962c803e3105a40a655c4cbd98`
