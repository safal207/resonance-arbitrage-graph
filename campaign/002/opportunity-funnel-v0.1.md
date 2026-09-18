# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `87cc0a2f08edc6bd37cc23e3234872ae8b2dfd7bf7fe9699aacc026fdb4e4111`
- Replay SHA-256: `3762f6f580bda7dbde11f954b8a2fc0458c8653e18cc6e63b525e3baf5370a5d`

## Cumulative funnel

- Captured terminal cycles: **1380**
- Complete evidence: **1378** (99.86%)
- Structural constraints pass: **1143** (82.83%)
- Gross-positive before costs: **183** (13.26%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -4.09 bps (min -40.61, max 10.88)**
- Expected net edge: **mean -40.03 bps (min -76.42, max -25.12)**
- Observed terminal edge: **mean -39.95 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.81, max 36.00)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 960 × `GROSS_NON_POSITIVE`
- 183 × `MODELED_COSTS_ERASE_EDGE`
- 135 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 53 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 47 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `5dda05675f19043fa207b3fb08d795e54cd6f1a7af36cb91c0880c643b849d6c`
