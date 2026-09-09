# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `6ce90cdf60cdb20e89516c3d7e30c6d8c6cf5be230c76e67a2911d181a0af03b`
- Replay SHA-256: `e6343f3190d97c872d94f4f448a300f867c9abaad474e62d486f9e703f2d49d1`

## Cumulative funnel

- Captured terminal cycles: **788**
- Complete evidence: **786** (99.75%)
- Structural constraints pass: **671** (85.15%)
- Gross-positive before costs: **119** (15.10%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -3.90 bps (min -35.06, max 8.52)**
- Expected net edge: **mean -39.85 bps (min -70.89, max -27.47)**
- Observed terminal edge: **mean -39.80 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.83, max 35.99)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 552 × `GROSS_NON_POSITIVE`
- 119 × `MODELED_COSTS_ERASE_EDGE`
- 65 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 26 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 24 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `361b79e215ef382b6a8a7f488c5029aba93276f49e9f5e122334773e29b05587`
