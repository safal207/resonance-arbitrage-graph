# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `3812b19eb70079891943115376d67f326c344497dec4e9c816cb71305934f528`
- Replay SHA-256: `a6994528eed80d28260f6295f350c04c23c9bd16e2eec2225a60f43b8044adfd`

## Cumulative funnel

- Captured terminal cycles: **220**
- Complete evidence: **220** (100.00%)
- Structural constraints pass: **193** (87.73%)
- Gross-positive before costs: **31** (14.09%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -4.19 bps (min -29.56, max 5.22)**
- Expected net edge: **mean -40.13 bps (min -65.41, max -30.75)**
- Observed terminal edge: **mean -40.19 bps (min -88.73, max -30.80)**
- Modeled cost drag: **mean 35.94 bps (min 35.85, max 35.98)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 162 × `GROSS_NON_POSITIVE`
- 31 × `MODELED_COSTS_ERASE_EDGE`
- 10 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 9 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 8 × `STRUCTURAL:CAPACITY_EXCEEDED:0`

Evidence SHA-256: `2f02c288a0838b5c4bdad4622ded5b9f11f4f612bc14c678273ac81e7816d377`
