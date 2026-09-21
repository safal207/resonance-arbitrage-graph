# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `a9941b495a3f25d3c9a7aa794434d20951e3c40f834a11617ed7fb7d6305b16d`
- Replay SHA-256: `e539aa89a0ace1edc86b9650328360eb30cde470ec74cfc7096bf02523513e21`

## Cumulative funnel

- Captured terminal cycles: **1570**
- Complete evidence: **1566** (99.75%)
- Structural constraints pass: **1307** (83.25%)
- Gross-positive before costs: **201** (12.80%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -4.20 bps (min -40.61, max 10.88)**
- Expected net edge: **mean -40.14 bps (min -76.42, max -25.12)**
- Observed terminal edge: **mean -40.07 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.81, max 36.00)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 1106 × `GROSS_NON_POSITIVE`
- 201 × `MODELED_COSTS_ERASE_EDGE`
- 151 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 55 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 53 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 4 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `484cd18202eaaed197f34eb6fb3b4ebd28277cf2dcb25ddb38489d078849b454`
