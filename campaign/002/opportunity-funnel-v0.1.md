# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `f10b51a11050cf726fc3a2e114354adb3fa639d31cc61c6fb94a090ac2d58f87`
- Replay SHA-256: `be056a47ac2b23d38e128bc816543fe75ff3248af14c4d141afd11d9ceceb9a2`

## Cumulative funnel

- Captured terminal cycles: **1170**
- Complete evidence: **1168** (99.83%)
- Structural constraints pass: **974** (83.25%)
- Gross-positive before costs: **168** (14.36%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -3.93 bps (min -35.06, max 8.52)**
- Expected net edge: **mean -39.87 bps (min -70.89, max -27.47)**
- Observed terminal edge: **mean -39.81 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.83, max 35.99)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 806 × `GROSS_NON_POSITIVE`
- 168 × `MODELED_COSTS_ERASE_EDGE`
- 119 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 39 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 36 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `c3be74d5c61400de33437b4fb7cd68cf85f9e32b40042f91f45461ef96440a3e`
