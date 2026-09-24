# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `4165e769cfd798f21085855a0a1756bf3f1ab7f712816527902e1a8f250dcb31`
- Replay SHA-256: `2d0c0a81e59058ac047668d26ca0c318d776a879aa0aaefbab59c133ab6937f4`

## Cumulative funnel

- Captured terminal cycles: **1710**
- Complete evidence: **1706** (99.77%)
- Structural constraints pass: **1420** (83.04%)
- Gross-positive before costs: **210** (12.28%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -4.24 bps (min -40.61, max 10.88)**
- Expected net edge: **mean -40.18 bps (min -76.42, max -25.12)**
- Observed terminal edge: **mean -40.11 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.81, max 36.00)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 1210 × `GROSS_NON_POSITIVE`
- 210 × `MODELED_COSTS_ERASE_EDGE`
- 163 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 62 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 61 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 4 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `45637f35307476715e9402f671dcb8340501a6116dacf7e52398c2571d755b1a`
