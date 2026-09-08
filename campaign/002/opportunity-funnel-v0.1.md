# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `ebf951b76cb28a54ede2f175e03c72847bdd31285f944a78a888fee5a51f5461`
- Replay SHA-256: `b0ad3bb6381683f2bc7cf6b157a98629c17006ac3bb5e58f16d47c4f128adc14`

## Cumulative funnel

- Captured terminal cycles: **718**
- Complete evidence: **716** (99.72%)
- Structural constraints pass: **614** (85.52%)
- Gross-positive before costs: **107** (14.90%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -3.89 bps (min -35.06, max 8.52)**
- Expected net edge: **mean -39.83 bps (min -70.89, max -27.47)**
- Observed terminal edge: **mean -39.78 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.83, max 35.99)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 507 × `GROSS_NON_POSITIVE`
- 107 × `MODELED_COSTS_ERASE_EDGE`
- 57 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 23 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 22 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `14b27972c45ed864512c8d9fcfd4a00795f016f5be94abaaed684d9a752cccda`
