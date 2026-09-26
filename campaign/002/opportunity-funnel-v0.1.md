# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `33909117135a1e268393c8995f4950bb9042d0a5c117bbef3330f96ccb5eae18`
- Replay SHA-256: `ade7a280985ec39548f3e53473d92e342d88dbaef428139bca44022932fe4be9`

## Cumulative funnel

- Captured terminal cycles: **1880**
- Complete evidence: **1876** (99.79%)
- Structural constraints pass: **1559** (82.93%)
- Gross-positive before costs: **220** (11.70%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -4.27 bps (min -40.61, max 10.88)**
- Expected net edge: **mean -40.21 bps (min -76.42, max -25.12)**
- Observed terminal edge: **mean -40.13 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.81, max 36.00)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 1339 × `GROSS_NON_POSITIVE`
- 220 × `MODELED_COSTS_ERASE_EDGE`
- 183 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 68 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 66 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 4 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `8ea927aa446db8b688a764b9a8e0d84d6835642c0b19d5977fc264215c29d8db`
