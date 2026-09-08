# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `e46262bf737e2cf3522477da93fcf9d59a46d364dab5f8fa89ef7fa7781c3bfb`
- Replay SHA-256: `a8e2e233499673f6b7432c178af6ce9f9baecc8192d84443bacee6daa63e41a8`

## Cumulative funnel

- Captured terminal cycles: **710**
- Complete evidence: **708** (99.72%)
- Structural constraints pass: **609** (85.77%)
- Gross-positive before costs: **107** (15.07%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -3.88 bps (min -35.06, max 8.52)**
- Expected net edge: **mean -39.82 bps (min -70.89, max -27.47)**
- Observed terminal edge: **mean -39.77 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.83, max 35.99)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 502 × `GROSS_NON_POSITIVE`
- 107 × `MODELED_COSTS_ERASE_EDGE`
- 55 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 23 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 21 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `d434bfbe40bf3f63e9d32cb6fa415250c8aa8c3114cbc8366ba9f2355f29f6ab`
