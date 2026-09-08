# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `7806b8505faa91c622fe260a1f12dfe52be840d14c812dd27cdea9cf7a135a2d`
- Replay SHA-256: `a7903df0513d31caaf4aa5e46c57a8d41916f94fddd7eea50e96d02aaeec6b7f`

## Cumulative funnel

- Captured terminal cycles: **690**
- Complete evidence: **688** (99.71%)
- Structural constraints pass: **594** (86.09%)
- Gross-positive before costs: **104** (15.07%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -3.86 bps (min -35.06, max 8.52)**
- Expected net edge: **mean -39.80 bps (min -70.89, max -27.47)**
- Observed terminal edge: **mean -39.76 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.83, max 35.99)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 490 × `GROSS_NON_POSITIVE`
- 104 × `MODELED_COSTS_ERASE_EDGE`
- 51 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 23 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 20 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `c89fc085f3815222ff42965da47907dcc0784a73c5b1d1516fe79192b05cd911`
