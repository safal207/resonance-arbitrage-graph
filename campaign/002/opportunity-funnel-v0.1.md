# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `6501a7faabf4cf1b65e45bfca7d30e9ff615d322a8c1312b20139241a9f8fe06`
- Replay SHA-256: `97109df60638a5c40d0fb4035d22647c2e4086f1171a1b0ba62c55a0c4591a97`

## Cumulative funnel

- Captured terminal cycles: **1350**
- Complete evidence: **1348** (99.85%)
- Structural constraints pass: **1119** (82.89%)
- Gross-positive before costs: **180** (13.33%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -4.07 bps (min -40.61, max 10.88)**
- Expected net edge: **mean -40.01 bps (min -76.42, max -25.12)**
- Observed terminal edge: **mean -39.94 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.81, max 36.00)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 939 × `GROSS_NON_POSITIVE`
- 180 × `MODELED_COSTS_ERASE_EDGE`
- 133 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 51 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 45 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `d09242962d76ca480ca990095d6c1e026dfa34e3b89285823f57ddfc0be4607f`
