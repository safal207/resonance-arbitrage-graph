# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `94421587e06735f637f97965409a8a99f7262786d12a3c2519c2516e19c0b94b`
- Replay SHA-256: `6e7535612457e11df7a9cfb7a5ac5ff393aaeadd5b94fa1850e06ee709b3c103`

## Cumulative funnel

- Captured terminal cycles: **1140**
- Complete evidence: **1138** (99.82%)
- Structural constraints pass: **950** (83.33%)
- Gross-positive before costs: **163** (14.30%)
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

- 787 × `GROSS_NON_POSITIVE`
- 163 × `MODELED_COSTS_ERASE_EDGE`
- 116 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 39 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 33 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `6346a0b64305b02d34ec530640a77ea921fb53c848853c4f53f756dea8bb3c98`
