# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `c8260e4046deddb0637c8f9f918e2bf0abb124f425c53d648cb96c5cfcbc1d1f`
- Replay SHA-256: `62aa4dc2c7cf320f36fc418802e9951305dbd7588d42f39f7ee3f248ca35d787`

## Cumulative funnel

- Captured terminal cycles: **908**
- Complete evidence: **906** (99.78%)
- Structural constraints pass: **766** (84.36%)
- Gross-positive before costs: **132** (14.54%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -3.97 bps (min -35.06, max 8.52)**
- Expected net edge: **mean -39.91 bps (min -70.89, max -27.47)**
- Observed terminal edge: **mean -39.85 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.83, max 35.99)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 634 × `GROSS_NON_POSITIVE`
- 132 × `MODELED_COSTS_ERASE_EDGE`
- 87 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 28 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 25 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `bf9b56bf3dc85d47992ef402bce30dd45450120ede2bf44034bddccb5e671944`
