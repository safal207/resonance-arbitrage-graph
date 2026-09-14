# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `d0729b63f64371f66cbe00002616a06385550155e0aeb4564aee4cd2d467d3d0`
- Replay SHA-256: `73d136986dbfc0e2aba51cce6ec1d326cf87f9429d18e4eb3972c1b4e0f1ef17`

## Cumulative funnel

- Captured terminal cycles: **1130**
- Complete evidence: **1128** (99.82%)
- Structural constraints pass: **943** (83.45%)
- Gross-positive before costs: **163** (14.42%)
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

- 780 × `GROSS_NON_POSITIVE`
- 163 × `MODELED_COSTS_ERASE_EDGE`
- 115 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 38 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 32 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `fcde4ca759c9844e4e1121dae121b79357568460a2d10212bf915da983bfcb6b`
