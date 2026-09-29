# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `38f243491a5ff74a330fba8fa146f26686c9ed6532631e1eaf87446660c5b2df`
- Replay SHA-256: `fe55368a06d3e32df2299a47a66ce5dbdcf055a33b8ae87cfa36babf4a888e08`

## Cumulative funnel

- Captured terminal cycles: **1980**
- Complete evidence: **1974** (99.70%)
- Structural constraints pass: **1640** (82.83%)
- Gross-positive before costs: **225** (11.36%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -4.28 bps (min -40.61, max 10.88)**
- Expected net edge: **mean -40.22 bps (min -76.42, max -25.12)**
- Observed terminal edge: **mean -40.15 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.81, max 36.00)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 1415 × `GROSS_NON_POSITIVE`
- 225 × `MODELED_COSTS_ERASE_EDGE`
- 191 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 72 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 71 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 6 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `0954ff67db1a7920110232efe8369c5099bed8c4af7168e4d2782075086cbd15`
