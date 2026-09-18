# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `5b7490a9826028c469953f99fe819a07f239320d6af085b92d90fce8675db577`
- Replay SHA-256: `2b913161a1a477a3d762e3be996e4b7efde6e775d5b71fd3fc7f297b164a8fe6`

## Cumulative funnel

- Captured terminal cycles: **1330**
- Complete evidence: **1328** (99.85%)
- Structural constraints pass: **1104** (83.01%)
- Gross-positive before costs: **180** (13.53%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -4.03 bps (min -40.61, max 10.88)**
- Expected net edge: **mean -39.97 bps (min -76.42, max -25.12)**
- Observed terminal edge: **mean -39.89 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.81, max 36.00)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 924 × `GROSS_NON_POSITIVE`
- 180 × `MODELED_COSTS_ERASE_EDGE`
- 131 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 51 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 42 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `510da80df25b11301c8f28e5dbdeb448e8ac8d033373315c20394ab16359b7d6`
