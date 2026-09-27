# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `2780e17e5f1ca0cd1e4e04ea82e42a888e762bcba3ca15d2605bd38165bba961`
- Replay SHA-256: `c032204697a0fc11a18b0f94dbb6cbeb118a40239b4c1b49e731af368a190eeb`

## Cumulative funnel

- Captured terminal cycles: **1910**
- Complete evidence: **1906** (99.79%)
- Structural constraints pass: **1583** (82.88%)
- Gross-positive before costs: **221** (11.57%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -4.26 bps (min -40.61, max 10.88)**
- Expected net edge: **mean -40.20 bps (min -76.42, max -25.12)**
- Observed terminal edge: **mean -40.12 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.81, max 36.00)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 1362 × `GROSS_NON_POSITIVE`
- 221 × `MODELED_COSTS_ERASE_EDGE`
- 188 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 69 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 66 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 4 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `919a45c23e12f4a0bbb81220d077ad3307f54f0fbd2984d7c8b78621126dcea4`
