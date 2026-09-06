# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `71732fe1eefd6b0ad19fa548c4df6555d94fb55774d2d754b9e4dde95c1269d2`
- Replay SHA-256: `f3e19fbb56a59ace40871ec3320046944a95691d47be31784314b9de4b53f1ba`

## Cumulative funnel

- Captured terminal cycles: **540**
- Complete evidence: **538** (99.63%)
- Structural constraints pass: **466** (86.30%)
- Gross-positive before costs: **79** (14.63%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -3.90 bps (min -35.06, max 8.52)**
- Expected net edge: **mean -39.84 bps (min -70.89, max -27.47)**
- Observed terminal edge: **mean -39.84 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.83, max 35.99)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 387 × `GROSS_NON_POSITIVE`
- 79 × `MODELED_COSTS_ERASE_EDGE`
- 37 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 18 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 17 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `e7b4856ca567e218a32cfdd01c8b9d77312c2cf7a068b18b6aea705499541cb6`
