# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `7d85ff78aaa83ee7bf7977084594717c1164825a61eba2598f742ee914ffdeb4`
- Replay SHA-256: `1f2e7b46a1c6d7a09775083423ed83b6f69c6d3e3559fe1802f1362c9e5fab96`

## Cumulative funnel

- Captured terminal cycles: **1460**
- Complete evidence: **1458** (99.86%)
- Structural constraints pass: **1215** (83.22%)
- Gross-positive before costs: **189** (12.95%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -4.10 bps (min -40.61, max 10.88)**
- Expected net edge: **mean -40.04 bps (min -76.42, max -25.12)**
- Observed terminal edge: **mean -39.96 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.81, max 36.00)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 1026 × `GROSS_NON_POSITIVE`
- 189 × `MODELED_COSTS_ERASE_EDGE`
- 141 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 54 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 48 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `e605048108afbcdf1784268a6a54f9193175c63fb096a0a63f9355386219fc1e`
