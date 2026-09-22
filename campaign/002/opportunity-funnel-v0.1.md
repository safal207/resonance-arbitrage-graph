# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `2c9f8a69b0b515f8932f6be18dd9d9b29ea4c726376515247588e7ee9e70838d`
- Replay SHA-256: `cba1087b53a4fb729fe4a8d829cffccdf5e7ac8787ea514865b3b85119082626`

## Cumulative funnel

- Captured terminal cycles: **1590**
- Complete evidence: **1586** (99.75%)
- Structural constraints pass: **1323** (83.21%)
- Gross-positive before costs: **201** (12.64%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -4.20 bps (min -40.61, max 10.88)**
- Expected net edge: **mean -40.14 bps (min -76.42, max -25.12)**
- Observed terminal edge: **mean -40.09 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.81, max 36.00)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 1122 × `GROSS_NON_POSITIVE`
- 201 × `MODELED_COSTS_ERASE_EDGE`
- 154 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 55 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 54 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 4 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `595207877c2231013d9612b6866b2451f5d360723ed413f0af03eb2a971533b1`
