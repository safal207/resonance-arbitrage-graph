# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `498552e7d307c6082a0fdb8a1422c24441a09ece0512c005fafb2c4f156bb997`
- Replay SHA-256: `8b78a63b105e2c66066e2b6ae31bd5dc6ee7a95dd184b430e5a886c5b9533f31`

## Cumulative funnel

- Captured terminal cycles: **1000**
- Complete evidence: **998** (99.80%)
- Structural constraints pass: **843** (84.30%)
- Gross-positive before costs: **148** (14.80%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -3.94 bps (min -35.06, max 8.52)**
- Expected net edge: **mean -39.88 bps (min -70.89, max -27.47)**
- Observed terminal edge: **mean -39.82 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.83, max 35.99)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 695 × `GROSS_NON_POSITIVE`
- 148 × `MODELED_COSTS_ERASE_EDGE`
- 96 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 31 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 28 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `1731f88f125209668d9ab9e55af9b4cf23e47674ed216b24fb7e13ed5d2e46cc`
