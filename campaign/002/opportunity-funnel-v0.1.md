# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `f861409e34b4e5be0afd4ee4ec9bad625fee19877df8d000e4ab3eae73926686`
- Replay SHA-256: `1d5cbb919bd9382f7deef243ffe9de31c47ba1ff3c51a9baeaefba05f9bb74db`

## Cumulative funnel

- Captured terminal cycles: **240**
- Complete evidence: **240** (100.00%)
- Structural constraints pass: **212** (88.33%)
- Gross-positive before costs: **34** (14.17%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -4.23 bps (min -29.56, max 5.22)**
- Expected net edge: **mean -40.17 bps (min -65.41, max -30.75)**
- Observed terminal edge: **mean -40.15 bps (min -88.73, max -30.80)**
- Modeled cost drag: **mean 35.94 bps (min 35.85, max 35.98)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 178 × `GROSS_NON_POSITIVE`
- 34 × `MODELED_COSTS_ERASE_EDGE`
- 11 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 9 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 8 × `STRUCTURAL:CAPACITY_EXCEEDED:0`

Evidence SHA-256: `b158e49fe91f474d70d56e82448308fc83fbaaa197a8638dc0492027b8e64ac0`
