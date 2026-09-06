# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `49ff32ce812d75799eb84ecc5ef1d0072c28c0f246f8f9bb8134866478c4da45`
- Replay SHA-256: `875a2d23e8953c8f87d0ba3e324f1256c220e2274ae28b6f0af3ae65e9895fcf`

## Cumulative funnel

- Captured terminal cycles: **560**
- Complete evidence: **558** (99.64%)
- Structural constraints pass: **481** (85.89%)
- Gross-positive before costs: **81** (14.46%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -3.87 bps (min -35.06, max 8.52)**
- Expected net edge: **mean -39.81 bps (min -70.89, max -27.47)**
- Observed terminal edge: **mean -39.81 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.83, max 35.99)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 400 × `GROSS_NON_POSITIVE`
- 81 × `MODELED_COSTS_ERASE_EDGE`
- 40 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 19 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 18 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `5c33c1b79bbd8f17cc8a989b8576b6e0c75110a663382454ddf106f15dde7088`
