# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `162f519136b5b89d2bdb1acc4ba21a4aae6cb71a3a757d7c5d0b800614267edf`
- Replay SHA-256: `eeb0d4a6f65c5f3c6fae4122516f36ae3b51bc8f5c6b8334e06cb896f972072c`

## Cumulative funnel

- Captured terminal cycles: **868**
- Complete evidence: **866** (99.77%)
- Structural constraints pass: **737** (84.91%)
- Gross-positive before costs: **128** (14.75%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -3.94 bps (min -35.06, max 8.52)**
- Expected net edge: **mean -39.88 bps (min -70.89, max -27.47)**
- Observed terminal edge: **mean -39.82 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.83, max 35.99)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 609 × `GROSS_NON_POSITIVE`
- 128 × `MODELED_COSTS_ERASE_EDGE`
- 78 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 27 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 24 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `642922bc857333d24060861ea4c0e59ba61748eb20c9520d6cae6b0700ed27f4`
