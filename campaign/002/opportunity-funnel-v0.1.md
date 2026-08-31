# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `b356445b1d80ec90bf6463f1921d55b7240e73ec0cc07440e37d7f02ca490b84`
- Replay SHA-256: `d4088af1dd2e29ce7c4d7cbc7ff39eb8a9c8074a481fa5302550fc6bf12d0f81`

## Cumulative funnel

- Captured terminal cycles: **160**
- Complete evidence: **160** (100.00%)
- Structural constraints pass: **144** (90.00%)
- Gross-positive before costs: **25** (15.62%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -4.24 bps (min -29.56, max 5.22)**
- Expected net edge: **mean -40.18 bps (min -65.41, max -30.75)**
- Observed terminal edge: **mean -40.28 bps (min -88.73, max -30.80)**
- Modeled cost drag: **mean 35.94 bps (min 35.85, max 35.98)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 119 × `GROSS_NON_POSITIVE`
- 25 × `MODELED_COSTS_ERASE_EDGE`
- 7 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 6 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 3 × `STRUCTURAL:CAPACITY_EXCEEDED:0`

Evidence SHA-256: `d730049c1ef0a246f5d8c99ec07b980ded65d9cf3ecea65ff42f927ed5a0eef2`
