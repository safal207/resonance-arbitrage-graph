# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `c7e7b1f6a7227b119881d16d5d777602d81963b4e65a2ecb48aeba5ba6591235`
- Replay SHA-256: `b7ccda9dcd5040644b7c36954c328a663fb5176be3e7a08cb9652cbdeffe7a1a`

## Cumulative funnel

- Captured terminal cycles: **1690**
- Complete evidence: **1686** (99.76%)
- Structural constraints pass: **1404** (83.08%)
- Gross-positive before costs: **210** (12.43%)
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

- 1194 × `GROSS_NON_POSITIVE`
- 210 × `MODELED_COSTS_ERASE_EDGE`
- 162 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 61 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 59 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 4 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `c6369361ba983e296f5ee913cd752efe1d28ca0aef0b864e7926775e04d0a57f`
