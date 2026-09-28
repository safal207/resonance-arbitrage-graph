# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `9aba242f396e3423a1b890388af1f01457d0c38e132ae685a7e7d2af5a569398`
- Replay SHA-256: `c8dfa19f762bd2e20da9be09720adf8603dfed584ebc823d40a8d8de6e05fdd1`

## Cumulative funnel

- Captured terminal cycles: **1950**
- Complete evidence: **1946** (99.79%)
- Structural constraints pass: **1613** (82.72%)
- Gross-positive before costs: **224** (11.49%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -4.27 bps (min -40.61, max 10.88)**
- Expected net edge: **mean -40.21 bps (min -76.42, max -25.12)**
- Observed terminal edge: **mean -40.14 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.81, max 36.00)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 1389 × `GROSS_NON_POSITIVE`
- 224 × `MODELED_COSTS_ERASE_EDGE`
- 191 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 71 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 71 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 4 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `0283b670d055364c08553de6315ea5394c324f7327a93a7a70926caaa9b45e5e`
