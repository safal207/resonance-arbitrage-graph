# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `e1e3c517ac5a54c82c7bb585cfc6e7dbccdf0e5589c0c34bfd6c672761413366`
- Replay SHA-256: `eb421b4d6f6567998930ea99887582126c478f1600c908b52e76f70666b1590a`

## Cumulative funnel

- Captured terminal cycles: **1120**
- Complete evidence: **1118** (99.82%)
- Structural constraints pass: **936** (83.57%)
- Gross-positive before costs: **163** (14.55%)
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

- 773 × `GROSS_NON_POSITIVE`
- 163 × `MODELED_COSTS_ERASE_EDGE`
- 114 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 37 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 31 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `b96ff7da3805442147f5bd535313dc1ba8734180ec2e67c5d3351620bf2e323b`
