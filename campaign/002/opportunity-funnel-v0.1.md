# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `8b82918036ef713dd34cc5aa364c09e97703a8c903f1e42669c8f1e656ead6ed`
- Replay SHA-256: `8fbefa2c11cc5a04ad76413f6a084e02397b81b202b3aa6a766241ebc5c5d4a0`

## Cumulative funnel

- Captured terminal cycles: **310**
- Complete evidence: **310** (100.00%)
- Structural constraints pass: **274** (88.39%)
- Gross-positive before costs: **42** (13.55%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -4.09 bps (min -29.56, max 8.52)**
- Expected net edge: **mean -40.04 bps (min -65.41, max -27.47)**
- Observed terminal edge: **mean -40.04 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.85, max 35.99)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 232 × `GROSS_NON_POSITIVE`
- 42 × `MODELED_COSTS_ERASE_EDGE`
- 15 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 11 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 10 × `STRUCTURAL:CAPACITY_EXCEEDED:0`

Evidence SHA-256: `b4a2e04067b37cf08d8a18515527df77c9dd1a5b328a83e713f6e0803281e25e`
