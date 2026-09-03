# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `8a8446ce098b857924097f40dc798477696022ad95d48a83bace947bb085416c`
- Replay SHA-256: `40eb12aa0783e2725936eaa05547c4774e03981f26329f630b5e4106ca40949b`

## Cumulative funnel

- Captured terminal cycles: **330**
- Complete evidence: **328** (99.39%)
- Structural constraints pass: **290** (87.88%)
- Gross-positive before costs: **44** (13.33%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -4.06 bps (min -29.56, max 8.52)**
- Expected net edge: **mean -40.00 bps (min -65.41, max -27.47)**
- Observed terminal edge: **mean -39.98 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.85, max 35.99)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 246 × `GROSS_NON_POSITIVE`
- 44 × `MODELED_COSTS_ERASE_EDGE`
- 16 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 11 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 11 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `708327358737fc2b0d81de3dc1fe1989dca88d27f025dbcf74b69b1d644792e3`
