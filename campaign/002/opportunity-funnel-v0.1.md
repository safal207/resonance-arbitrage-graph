# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `9f8369b2a8153541c44a47d35f19835b8ae61b7af3f46f5e16c4f02db4bb7ccf`
- Replay SHA-256: `33c7f069122c41c12787f5006e3edab613deaef06c58180d04cb8f6ca3c91edf`

## Cumulative funnel

- Captured terminal cycles: **1810**
- Complete evidence: **1806** (99.78%)
- Structural constraints pass: **1500** (82.87%)
- Gross-positive before costs: **216** (11.93%)
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

- 1284 × `GROSS_NON_POSITIVE`
- 216 × `MODELED_COSTS_ERASE_EDGE`
- 177 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 65 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 64 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 4 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `742cbaa058c87033286fe8cccbb5a1dcf9cddf93c1d184b4e16bbe504b2af0c0`
