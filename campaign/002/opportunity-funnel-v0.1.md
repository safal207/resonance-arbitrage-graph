# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `34b94e716a994e9cd2297b04cd49f7f981e2c11fa8a91afea06437e3c68d2fba`
- Replay SHA-256: `de6ebbfc0336da1bdcf9d3be449adccd9292f3bc08313fdc7b66beb62ef263d4`

## Cumulative funnel

- Captured terminal cycles: **1210**
- Complete evidence: **1208** (99.83%)
- Structural constraints pass: **1001** (82.73%)
- Gross-positive before costs: **170** (14.05%)
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

- 831 × `GROSS_NON_POSITIVE`
- 170 × `MODELED_COSTS_ERASE_EDGE`
- 125 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 43 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 39 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `e87c952a61a32ce4b68d65ff2d5815d8ffa0831ddc6234090f791a1aa4b54ff2`
