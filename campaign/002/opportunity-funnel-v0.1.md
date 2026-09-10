# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `53a75b193053d628b5b9f0c224a204a34a49ea2b8460c50b46c528238e3d3f83`
- Replay SHA-256: `55655d24efe2f370832fc55fd093527fb1ce8e52589ae6b817f3d5b18f39d5ac`

## Cumulative funnel

- Captured terminal cycles: **838**
- Complete evidence: **836** (99.76%)
- Structural constraints pass: **708** (84.49%)
- Gross-positive before costs: **123** (14.68%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -3.92 bps (min -35.06, max 8.52)**
- Expected net edge: **mean -39.86 bps (min -70.89, max -27.47)**
- Observed terminal edge: **mean -39.81 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.83, max 35.99)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 585 × `GROSS_NON_POSITIVE`
- 123 × `MODELED_COSTS_ERASE_EDGE`
- 77 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 27 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 24 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `3886effe8b2902b5bd7422812d37e77a071292df2343119d1b67c77270bc767e`
