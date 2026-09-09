# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `3477b577c3d6378455a463f3545ee38e7ee1f955f7763c4654b15556f70b77d2`
- Replay SHA-256: `f24cd7fded91608f4d71dcac1f50856d7915ec1cb94b91f7bb85309fc09c42aa`

## Cumulative funnel

- Captured terminal cycles: **748**
- Complete evidence: **746** (99.73%)
- Structural constraints pass: **640** (85.56%)
- Gross-positive before costs: **113** (15.11%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -3.90 bps (min -35.06, max 8.52)**
- Expected net edge: **mean -39.84 bps (min -70.89, max -27.47)**
- Observed terminal edge: **mean -39.80 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.83, max 35.99)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 527 × `GROSS_NON_POSITIVE`
- 113 × `MODELED_COSTS_ERASE_EDGE`
- 58 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 25 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 23 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `01457b3b0d03d9b940940787fce09c407b89c7639eddbdb9d30c9c4efa119b1b`
