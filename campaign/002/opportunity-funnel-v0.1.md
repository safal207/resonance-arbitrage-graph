# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `4db0e5171c1b5de49acbc1a3eaf992c68a6c4075e8b8933bec5d5d3ca5f5c8b7`
- Replay SHA-256: `bb0e5c1e68dc90f87cbe85129936af20b4d66a001d3b35968a974ca5b7687563`

## Cumulative funnel

- Captured terminal cycles: **1430**
- Complete evidence: **1428** (99.86%)
- Structural constraints pass: **1190** (83.22%)
- Gross-positive before costs: **187** (13.08%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -4.09 bps (min -40.61, max 10.88)**
- Expected net edge: **mean -40.03 bps (min -76.42, max -25.12)**
- Observed terminal edge: **mean -39.95 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.81, max 36.00)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 1003 × `GROSS_NON_POSITIVE`
- 187 × `MODELED_COSTS_ERASE_EDGE`
- 137 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 53 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 48 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `ab00c76f248eb86a2a76b3010e95b0600638783724a98aab7e2826fe44150939`
