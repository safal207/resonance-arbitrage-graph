# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `bc7fc782579a625118f154b0f5464acbee15c94dd446ad08f39b6520fcb55bc4`
- Replay SHA-256: `d1fedcc624be80b8430e794f757ef03bba084286c1857d56d681d29781e5669b`

## Cumulative funnel

- Captured terminal cycles: **600**
- Complete evidence: **598** (99.67%)
- Structural constraints pass: **515** (85.83%)
- Gross-positive before costs: **88** (14.67%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -3.88 bps (min -35.06, max 8.52)**
- Expected net edge: **mean -39.83 bps (min -70.89, max -27.47)**
- Observed terminal edge: **mean -39.82 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.83, max 35.99)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 427 × `GROSS_NON_POSITIVE`
- 88 × `MODELED_COSTS_ERASE_EDGE`
- 44 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 21 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 18 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `a374a587d5e6d076a39fc16735469042f7ebe74bdd7b34db58a4b2427fde3edd`
