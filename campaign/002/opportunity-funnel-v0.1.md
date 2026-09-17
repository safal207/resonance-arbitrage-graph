# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `f8588c68c9bc2cb88aa3fd430247c6707ab91dc4c7253a3a342b37577a549a5b`
- Replay SHA-256: `cd90a643392721317986914b26de1b1617575537dbb2e1ee0cbae7ba2c6bb166`

## Cumulative funnel

- Captured terminal cycles: **1300**
- Complete evidence: **1298** (99.85%)
- Structural constraints pass: **1080** (83.08%)
- Gross-positive before costs: **179** (13.77%)
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

- 901 × `GROSS_NON_POSITIVE`
- 179 × `MODELED_COSTS_ERASE_EDGE`
- 129 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 49 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 40 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `27906d3339ecd6bf7698ff0f912c11f9269dee0cff02e0fb8175ae77761ba602`
