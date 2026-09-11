# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `932a16240aba881b2488d49aebc0824a06de4d2e054bef11f503e280a9a7be35`
- Replay SHA-256: `f26736deb47e02402cc2fcca0dcfbb190487ab2320ded4a2e0fe91e4865a0082`

## Cumulative funnel

- Captured terminal cycles: **928**
- Complete evidence: **926** (99.78%)
- Structural constraints pass: **784** (84.48%)
- Gross-positive before costs: **138** (14.87%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -3.96 bps (min -35.06, max 8.52)**
- Expected net edge: **mean -39.91 bps (min -70.89, max -27.47)**
- Observed terminal edge: **mean -39.84 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.83, max 35.99)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 646 × `GROSS_NON_POSITIVE`
- 138 × `MODELED_COSTS_ERASE_EDGE`
- 87 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 29 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 26 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `eefc5e4bcccd9477dda718226c4668fe0e91beec68fc96c6c3817b414333584c`
