# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `5b98bd693481653b1487ee4dc266faab00a410c1f3cb4bebaa93b318c734f7b2`
- Replay SHA-256: `46ee395efba655d9feef5c2ab5b010b8b92cc71ca70a4f6281441cf0d82024d1`

## Cumulative funnel

- Captured terminal cycles: **758**
- Complete evidence: **756** (99.74%)
- Structural constraints pass: **647** (85.36%)
- Gross-positive before costs: **114** (15.04%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -3.89 bps (min -35.06, max 8.52)**
- Expected net edge: **mean -39.83 bps (min -70.89, max -27.47)**
- Observed terminal edge: **mean -39.80 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.83, max 35.99)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 533 × `GROSS_NON_POSITIVE`
- 114 × `MODELED_COSTS_ERASE_EDGE`
- 61 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 25 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 23 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `aae20ca5033b6ad8ac0494e1427853e7efda9fcf35a128a510a4b4e502e483a9`
