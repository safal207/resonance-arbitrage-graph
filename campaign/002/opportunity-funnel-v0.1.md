# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `324c3dff6f79707f3ed640d53083a2efaed4caa94da86e5eeb1b263d1775b686`
- Replay SHA-256: `c9e39155d80ae17522cc7f5e591e483e6cbb55d693e6c9f85ab40573ec36ed12`

## Cumulative funnel

- Captured terminal cycles: **1670**
- Complete evidence: **1666** (99.76%)
- Structural constraints pass: **1387** (83.05%)
- Gross-positive before costs: **206** (12.34%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -4.23 bps (min -40.61, max 10.88)**
- Expected net edge: **mean -40.18 bps (min -76.42, max -25.12)**
- Observed terminal edge: **mean -40.10 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.81, max 36.00)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 1181 × `GROSS_NON_POSITIVE`
- 206 × `MODELED_COSTS_ERASE_EDGE`
- 161 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 61 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 57 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 4 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `ff24805bb0b7a1c2210e01f1d3277b20e223ada46afcfd52a0325bf0be7ee7e3`
