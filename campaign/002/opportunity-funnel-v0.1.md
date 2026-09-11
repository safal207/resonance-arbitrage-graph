# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `5cdf28252f2bc1ca995650be5663fda51b0fd9d932350d571b9b6194379bd336`
- Replay SHA-256: `41eba5ca05d1cebbcd960d7e665c20f4d93a109ef8492ff31686870ded8d388f`

## Cumulative funnel

- Captured terminal cycles: **898**
- Complete evidence: **896** (99.78%)
- Structural constraints pass: **758** (84.41%)
- Gross-positive before costs: **130** (14.48%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -3.93 bps (min -35.06, max 8.52)**
- Expected net edge: **mean -39.88 bps (min -70.89, max -27.47)**
- Observed terminal edge: **mean -39.81 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.83, max 35.99)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 628 × `GROSS_NON_POSITIVE`
- 130 × `MODELED_COSTS_ERASE_EDGE`
- 86 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 27 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 25 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `eb4e1d09ab85458609feaf1354a8e238e95c513e6d5ff87335c868fa63bcbe91`
