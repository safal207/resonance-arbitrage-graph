# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `dedfe33d3fce63e2d105da5c8d8c2798a8002cf76282b28de01967b5967e97ab`
- Replay SHA-256: `a7814707ab196a1edf56a8c6cd8b9aca6ebc691dff32566c843cf5f246da20f2`

## Cumulative funnel

- Captured terminal cycles: **1680**
- Complete evidence: **1676** (99.76%)
- Structural constraints pass: **1394** (82.98%)
- Gross-positive before costs: **208** (12.38%)
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

- 1186 × `GROSS_NON_POSITIVE`
- 208 × `MODELED_COSTS_ERASE_EDGE`
- 162 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 61 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 59 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 4 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `59ed6a5edb1ad1e56852f24095cc3a243b356a4a7c31e3957406148273b58a5b`
