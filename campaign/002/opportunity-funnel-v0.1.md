# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `11a4ddad13445a43441f08f60cf06edbe1b0724e8f9236f8f9e19deb858ae3ec`
- Replay SHA-256: `4e095abd82ee9228656b28fdecbac7e320d54c39d2f815e061e51bce7ded5ee2`

## Cumulative funnel

- Captured terminal cycles: **1010**
- Complete evidence: **1008** (99.80%)
- Structural constraints pass: **849** (84.06%)
- Gross-positive before costs: **148** (14.65%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -3.92 bps (min -35.06, max 8.52)**
- Expected net edge: **mean -39.87 bps (min -70.89, max -27.47)**
- Observed terminal edge: **mean -39.81 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.83, max 35.99)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 701 × `GROSS_NON_POSITIVE`
- 148 × `MODELED_COSTS_ERASE_EDGE`
- 99 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 32 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 28 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `b90b115293d3d90f29e4786a6dac82f015f1b4f9fa425d02964a8a8787cb5216`
