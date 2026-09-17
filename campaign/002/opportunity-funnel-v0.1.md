# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `75b447ec3ccd858f3da3e966fc59156eadfe4cb3b7eb8b971c341b66e5597b1b`
- Replay SHA-256: `c814b4b736035fed8ae0464d794c51846a8005c86f38f3357679359ecb9f0a53`

## Cumulative funnel

- Captured terminal cycles: **1290**
- Complete evidence: **1288** (99.84%)
- Structural constraints pass: **1070** (82.95%)
- Gross-positive before costs: **178** (13.80%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -3.99 bps (min -35.06, max 8.52)**
- Expected net edge: **mean -39.93 bps (min -70.89, max -27.47)**
- Observed terminal edge: **mean -39.87 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.83, max 35.99)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 892 × `GROSS_NON_POSITIVE`
- 178 × `MODELED_COSTS_ERASE_EDGE`
- 129 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 49 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 40 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `f9343efe6af7cb96a2d5cee4661aee558fe39f87c850d3ac1fb57a9e1eaafb77`
