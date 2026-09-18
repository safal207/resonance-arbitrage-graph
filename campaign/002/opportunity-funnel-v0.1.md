# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `f2831c04fcd8061b8a9d68f7f9f4a5ca28f994ae920c935b133d65ffc96e6a4e`
- Replay SHA-256: `f0a652ef10d2828473aaaaa81d2bdee520daa8504d66bf01f235336a882407ab`

## Cumulative funnel

- Captured terminal cycles: **1340**
- Complete evidence: **1338** (99.85%)
- Structural constraints pass: **1113** (83.06%)
- Gross-positive before costs: **180** (13.43%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -4.04 bps (min -40.61, max 10.88)**
- Expected net edge: **mean -39.98 bps (min -76.42, max -25.12)**
- Observed terminal edge: **mean -39.91 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.81, max 36.00)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 933 × `GROSS_NON_POSITIVE`
- 180 × `MODELED_COSTS_ERASE_EDGE`
- 131 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 51 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 43 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `cabe4863c2f5e21339e6749b10e9287282dd87143a790a08edaec4be43b4bf9e`
