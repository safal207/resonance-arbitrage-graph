# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `0d93119ec86839c368efa1e2379841c0ce6fb30afc2b011bb2b03e3eccd21951`
- Replay SHA-256: `2395cbddfbac02bd32a0eedc397869a0c89675a6cef9285315119da5b1674b0b`

## Cumulative funnel

- Captured terminal cycles: **970**
- Complete evidence: **968** (99.79%)
- Structural constraints pass: **818** (84.33%)
- Gross-positive before costs: **145** (14.95%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -3.94 bps (min -35.06, max 8.52)**
- Expected net edge: **mean -39.89 bps (min -70.89, max -27.47)**
- Observed terminal edge: **mean -39.82 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.83, max 35.99)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 673 × `GROSS_NON_POSITIVE`
- 145 × `MODELED_COSTS_ERASE_EDGE`
- 93 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 30 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 27 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `aa464bb8dcc44ab8dd60307119b5487c65a895662f68aa936cfd0836efcb0f26`
