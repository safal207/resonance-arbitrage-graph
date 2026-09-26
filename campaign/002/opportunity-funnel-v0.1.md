# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `96264e7e94e764a1090170e5268981c7676aef505638a368f71ab578888763d0`
- Replay SHA-256: `9618353dad0d72e55b0500af76ec4a9945302cc8afc04e8144d41884c43af545`

## Cumulative funnel

- Captured terminal cycles: **1830**
- Complete evidence: **1826** (99.78%)
- Structural constraints pass: **1516** (82.84%)
- Gross-positive before costs: **218** (11.91%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -4.25 bps (min -40.61, max 10.88)**
- Expected net edge: **mean -40.19 bps (min -76.42, max -25.12)**
- Observed terminal edge: **mean -40.13 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.81, max 36.00)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 1298 × `GROSS_NON_POSITIVE`
- 218 × `MODELED_COSTS_ERASE_EDGE`
- 178 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 67 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 65 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 4 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `02ddc8e0628701fad5f79f14a5843431b9e58e6a1e984ef2947a33bd41f8b4bc`
