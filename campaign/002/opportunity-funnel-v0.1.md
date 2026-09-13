# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `2b176f5b9a8a4c13059208cd398cef1a2832306bb3bde35d8e6d94958022f07c`
- Replay SHA-256: `7262e9137797fea5722319976e9429db7a7012f6de593dcd6d644e41739f0484`

## Cumulative funnel

- Captured terminal cycles: **1060**
- Complete evidence: **1058** (99.81%)
- Structural constraints pass: **891** (84.06%)
- Gross-positive before costs: **156** (14.72%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -3.91 bps (min -35.06, max 8.52)**
- Expected net edge: **mean -39.86 bps (min -70.89, max -27.47)**
- Observed terminal edge: **mean -39.80 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.83, max 35.99)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 735 × `GROSS_NON_POSITIVE`
- 156 × `MODELED_COSTS_ERASE_EDGE`
- 105 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 33 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 29 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `08d04d595e1b8baa99da35a94233a0d13de9cccc2e86c728ae89cb21d410ee8c`
