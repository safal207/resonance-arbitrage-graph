# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `e71393544b229f9885b04cbfe2de59af0b1c8ec2341018cc1dfbd73318174c46`
- Replay SHA-256: `d63db1b787e41b8f78c771aed19d9a8aa062945406083eb44a74bf887c162859`

## Cumulative funnel

- Captured terminal cycles: **1800**
- Complete evidence: **1796** (99.78%)
- Structural constraints pass: **1491** (82.83%)
- Gross-positive before costs: **215** (11.94%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -4.25 bps (min -40.61, max 10.88)**
- Expected net edge: **mean -40.19 bps (min -76.42, max -25.12)**
- Observed terminal edge: **mean -40.12 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.81, max 36.00)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 1276 × `GROSS_NON_POSITIVE`
- 215 × `MODELED_COSTS_ERASE_EDGE`
- 176 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 65 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 64 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 4 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `2d7f1a28a1f5838f119a8ca204ec0768be6981e8ca1ec4dc3891763046343d3f`
