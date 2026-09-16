# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `8f5e3ff1e7408e4503160f9ca8f6b2e381367986319ead3ccf63d0e4942d3b09`
- Replay SHA-256: `387a60cc82215c4fc9b3159b91d7f12eb06d097cc992c036d73504d4ee4d6d92`

## Cumulative funnel

- Captured terminal cycles: **1220**
- Complete evidence: **1218** (99.84%)
- Structural constraints pass: **1009** (82.70%)
- Gross-positive before costs: **171** (14.02%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -3.97 bps (min -35.06, max 8.52)**
- Expected net edge: **mean -39.91 bps (min -70.89, max -27.47)**
- Observed terminal edge: **mean -39.83 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.83, max 35.99)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 838 × `GROSS_NON_POSITIVE`
- 171 × `MODELED_COSTS_ERASE_EDGE`
- 127 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 43 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 39 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `41be398617f6b2729540869261f971b858dcfb9973dd24346cdbb53efffd86fa`
