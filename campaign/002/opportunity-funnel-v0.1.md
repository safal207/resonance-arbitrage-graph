# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `3ef760948e103d8acc07190a3e69cf541883acf06198933ae343e58d229303db`
- Replay SHA-256: `b1d59bbac015f679133712bdbb57ddaceee7ce979b4bfbae6d15b1be1f781ccd`

## Cumulative funnel

- Captured terminal cycles: **1520**
- Complete evidence: **1518** (99.87%)
- Structural constraints pass: **1265** (83.22%)
- Gross-positive before costs: **193** (12.70%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -4.19 bps (min -40.61, max 10.88)**
- Expected net edge: **mean -40.14 bps (min -76.42, max -25.12)**
- Observed terminal edge: **mean -40.04 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.81, max 36.00)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 1072 × `GROSS_NON_POSITIVE`
- 193 × `MODELED_COSTS_ERASE_EDGE`
- 149 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 54 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 50 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `ee91bfd30bbf4b3c922805dcbcca23e49030700b3ab16d3dd15b56a95eb29bb3`
