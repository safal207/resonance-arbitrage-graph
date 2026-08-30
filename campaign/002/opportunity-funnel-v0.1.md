# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `c59e335dc3c2596f4359a96d39ee2d29a8ef7d8bff10039e44bb7dffc6ed2ce4`
- Replay SHA-256: `8b8d10b058fc1b96fa8957a7f02286e6e10389055d599277ec3a33dfd3de723e`

## Cumulative funnel

- Captured terminal cycles: **90**
- Complete evidence: **90** (100.00%)
- Structural constraints pass: **81** (90.00%)
- Gross-positive before costs: **14** (15.56%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -4.01 bps (min -29.56, max 5.22)**
- Expected net edge: **mean -39.95 bps (min -65.41, max -30.75)**
- Observed terminal edge: **mean -40.39 bps (min -88.73, max -30.80)**
- Modeled cost drag: **mean 35.94 bps (min 35.85, max 35.98)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 67 × `GROSS_NON_POSITIVE`
- 14 × `MODELED_COSTS_ERASE_EDGE`
- 4 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 4 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 1 × `STRUCTURAL:CAPACITY_EXCEEDED:0`

Evidence SHA-256: `dc5f7c38a10f4bca0056015b0e89457204c13cca14ae913bdc350bfd21f03d47`
