# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `606a3777ed37be08cf3527c8a2701eedf0525af55f580ca4339dd86321bb5263`
- Replay SHA-256: `64fcd8171a7cb7c0688e2a5038806eff81906a21ee20356f3d27e92ddf1253dd`

## Cumulative funnel

- Captured terminal cycles: **610**
- Complete evidence: **608** (99.67%)
- Structural constraints pass: **525** (86.07%)
- Gross-positive before costs: **89** (14.59%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -3.87 bps (min -35.06, max 8.52)**
- Expected net edge: **mean -39.82 bps (min -70.89, max -27.47)**
- Observed terminal edge: **mean -39.81 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.83, max 35.99)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 436 × `GROSS_NON_POSITIVE`
- 89 × `MODELED_COSTS_ERASE_EDGE`
- 44 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 21 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 18 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `951665f96e673007732d43733ee877bfe1260123a7e3f62996dbbbdd32fa6e27`
