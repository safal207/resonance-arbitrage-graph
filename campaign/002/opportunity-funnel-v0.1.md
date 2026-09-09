# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `d0225aa66a441b1035a2add9d15b7252c51b5b3f75df19b231466beccc414870`
- Replay SHA-256: `f6c69d60d9b0a6d1a5d7d49e0c2dbe6238ccc8c48f2abb97d9f8a0ae7765cff4`

## Cumulative funnel

- Captured terminal cycles: **768**
- Complete evidence: **766** (99.74%)
- Structural constraints pass: **654** (85.16%)
- Gross-positive before costs: **115** (14.97%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -3.90 bps (min -35.06, max 8.52)**
- Expected net edge: **mean -39.84 bps (min -70.89, max -27.47)**
- Observed terminal edge: **mean -39.80 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.83, max 35.99)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 539 × `GROSS_NON_POSITIVE`
- 115 × `MODELED_COSTS_ERASE_EDGE`
- 63 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 25 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 24 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `8fd18f5c4f5673de4116d210e6bbc416f883953fb78a6ecbd54bd883b96494b7`
