# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `58afb67de589c6c7eded5dd6195cd19f03e6d31aff9a507cb9bec4b86c305366`
- Replay SHA-256: `6d48667f65e1b4b7b446b85d9a5b80920019b4f49a69b513eaa8ee9a26e05cd6`

## Cumulative funnel

- Captured terminal cycles: **1230**
- Complete evidence: **1228** (99.84%)
- Structural constraints pass: **1017** (82.68%)
- Gross-positive before costs: **172** (13.98%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -3.98 bps (min -35.06, max 8.52)**
- Expected net edge: **mean -39.92 bps (min -70.89, max -27.47)**
- Observed terminal edge: **mean -39.84 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.83, max 35.99)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 845 × `GROSS_NON_POSITIVE`
- 172 × `MODELED_COSTS_ERASE_EDGE`
- 127 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 45 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 39 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `6a1a01fd9862a681d2ecdf22aaa258113ad93d1b8b7ca65f8b59b6cac94915f2`
