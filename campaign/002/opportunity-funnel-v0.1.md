# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `f5fa11d3f21a06d987e83715005ddf30e345a5bc1424c95c36ffd48a0790dc66`
- Replay SHA-256: `aa96a46460572feb143191909af9dc7857390e9afd8c3aa1976bb2a1d82815a3`

## Cumulative funnel

- Captured terminal cycles: **70**
- Complete evidence: **70** (100.00%)
- Structural constraints pass: **64** (91.43%)
- Gross-positive before costs: **11** (15.71%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -3.91 bps (min -19.95, max 5.22)**
- Expected net edge: **mean -39.85 bps (min -55.84, max -30.75)**
- Observed terminal edge: **mean -39.93 bps (min -57.05, max -30.80)**
- Modeled cost drag: **mean 35.94 bps (min 35.89, max 35.98)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 53 × `GROSS_NON_POSITIVE`
- 11 × `MODELED_COSTS_ERASE_EDGE`
- 3 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 2 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 1 × `STRUCTURAL:CAPACITY_EXCEEDED:0`

Evidence SHA-256: `ca6897a6eda69fbd1a5e67437dd679954fb89041f158cf7399d5d06f690433b3`
