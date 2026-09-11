# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `5855a4420c96e70f8de9afad8ad92b3ab01ef4c875a6fb46ba0191007b291b77`
- Replay SHA-256: `a9d403462a1e1a3d567fad5a4bdf049f8743f243d786b384ed9ab9a5a0dbd178`

## Cumulative funnel

- Captured terminal cycles: **918**
- Complete evidence: **916** (99.78%)
- Structural constraints pass: **776** (84.53%)
- Gross-positive before costs: **135** (14.71%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -3.97 bps (min -35.06, max 8.52)**
- Expected net edge: **mean -39.91 bps (min -70.89, max -27.47)**
- Observed terminal edge: **mean -39.84 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.83, max 35.99)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 641 × `GROSS_NON_POSITIVE`
- 135 × `MODELED_COSTS_ERASE_EDGE`
- 87 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 28 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 25 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `26772d6d26a9282876e7d89c77189705c6c40f81ffe674cae00ce2f487681272`
