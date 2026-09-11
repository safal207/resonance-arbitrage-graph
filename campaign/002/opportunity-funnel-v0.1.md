# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `2e30c77b072f46080d9cc728c8304558b5fac165f975f631e435487ed24a120d`
- Replay SHA-256: `b64b0da16cc6e1f7f9ec8b20be4ac3803e580da249b20a98b8c4c501996cc297`

## Cumulative funnel

- Captured terminal cycles: **938**
- Complete evidence: **936** (99.79%)
- Structural constraints pass: **793** (84.54%)
- Gross-positive before costs: **140** (14.93%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -3.96 bps (min -35.06, max 8.52)**
- Expected net edge: **mean -39.90 bps (min -70.89, max -27.47)**
- Observed terminal edge: **mean -39.84 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.83, max 35.99)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 653 × `GROSS_NON_POSITIVE`
- 140 × `MODELED_COSTS_ERASE_EDGE`
- 87 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 29 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 27 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `d9fb1e9a5e45a93f7d85437df0ccc3e4e6be1cc083aecadaf24e480098406bf1`
