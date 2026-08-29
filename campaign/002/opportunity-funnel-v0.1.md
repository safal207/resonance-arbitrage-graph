# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `30db7b133da15417b49bc21c43593e1aaf5ac1482ae192b87bc85fde1797b733`
- Replay SHA-256: `74897fcf8d8f0f0e00263691405d1968fbe482a80ad3df755a2efcca06e18701`

## Cumulative funnel

- Captured terminal cycles: **20**
- Complete evidence: **20** (100.00%)
- Structural constraints pass: **19** (95.00%)
- Gross-positive before costs: **2** (10.00%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -4.23 bps (min -14.03, max 1.65)**
- Expected net edge: **mean -40.17 bps (min -49.93, max -34.31)**
- Observed terminal edge: **mean -40.10 bps (min -49.93, max -30.80)**
- Modeled cost drag: **mean 35.94 bps (min 35.91, max 35.96)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 17 × `GROSS_NON_POSITIVE`
- 2 × `MODELED_COSTS_ERASE_EDGE`
- 1 × `STRUCTURAL:CAPACITY_EXCEEDED:1`

Evidence SHA-256: `4cfc07bb0451a7566cc4aee1fdbc59fd20d766731a885ff356dfe70d1cc1727b`
