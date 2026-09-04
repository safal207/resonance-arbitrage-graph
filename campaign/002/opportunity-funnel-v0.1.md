# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `3f91f913a8b6c1afb9002510df8251f39de1a3023caed803d2475e8fdedd2ef9`
- Replay SHA-256: `de0392d79bbfc79c60546b78173d6872351adf208469017f70c0d7990e819726`

## Cumulative funnel

- Captured terminal cycles: **380**
- Complete evidence: **378** (99.47%)
- Structural constraints pass: **332** (87.37%)
- Gross-positive before costs: **50** (13.16%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -4.02 bps (min -29.56, max 8.52)**
- Expected net edge: **mean -39.97 bps (min -65.41, max -27.47)**
- Observed terminal edge: **mean -39.97 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.85, max 35.99)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 282 × `GROSS_NON_POSITIVE`
- 50 × `MODELED_COSTS_ERASE_EDGE`
- 24 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 11 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 11 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `4f8cd78517cdbfebc448c5d528bd316d1d2e8a29f66b6bf7091e6fd894769f09`
