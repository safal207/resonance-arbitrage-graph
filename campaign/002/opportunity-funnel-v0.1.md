# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `167353df76e06626b9fa2fe8c1e5f8380e6cfb2781c9fe05e8bd2670bfa57302`
- Replay SHA-256: `c434ef9ac7c62d15c81e9927e9f7139b0b8e31f27fe65a5e8f22732da01986b1`

## Cumulative funnel

- Captured terminal cycles: **1900**
- Complete evidence: **1896** (99.79%)
- Structural constraints pass: **1574** (82.84%)
- Gross-positive before costs: **221** (11.63%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -4.26 bps (min -40.61, max 10.88)**
- Expected net edge: **mean -40.20 bps (min -76.42, max -25.12)**
- Observed terminal edge: **mean -40.13 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.81, max 36.00)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 1353 × `GROSS_NON_POSITIVE`
- 221 × `MODELED_COSTS_ERASE_EDGE`
- 187 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 69 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 66 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 4 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `a863b39ad3415c1ac8cea51ec89dfaff0aa14b08e2a959020935da497fb00115`
