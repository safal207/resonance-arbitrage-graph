# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `a70bc271c8e8a12c54d4ec332008d09efadfff878c875b6a1677d77bb3ed8337`
- Replay SHA-256: `1c766aac831821ffbccf9baba03d7ed3bfb8b237ee6a55e725d7dfd713eaf4e2`

## Cumulative funnel

- Captured terminal cycles: **1470**
- Complete evidence: **1468** (99.86%)
- Structural constraints pass: **1224** (83.27%)
- Gross-positive before costs: **189** (12.86%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -4.10 bps (min -40.61, max 10.88)**
- Expected net edge: **mean -40.05 bps (min -76.42, max -25.12)**
- Observed terminal edge: **mean -39.98 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.81, max 36.00)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 1035 × `GROSS_NON_POSITIVE`
- 189 × `MODELED_COSTS_ERASE_EDGE`
- 142 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 54 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 48 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `b2dae1f25dfad8cf8bddda0adfbac6b4a75308c7bfb26e0653e6fac110cc94fb`
