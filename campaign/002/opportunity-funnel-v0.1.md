# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `530ccdcabfe94ae79f9df49131a622ff101f6e8341f576bfd2bd0230b9e0c6f4`
- Replay SHA-256: `3d3da2a4c1b1141be1e62981706c62c536de422c26851e19f139998dac051224`

## Cumulative funnel

- Captured terminal cycles: **1440**
- Complete evidence: **1438** (99.86%)
- Structural constraints pass: **1199** (83.26%)
- Gross-positive before costs: **188** (13.06%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -4.09 bps (min -40.61, max 10.88)**
- Expected net edge: **mean -40.03 bps (min -76.42, max -25.12)**
- Observed terminal edge: **mean -39.95 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.81, max 36.00)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 1011 × `GROSS_NON_POSITIVE`
- 188 × `MODELED_COSTS_ERASE_EDGE`
- 138 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 53 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 48 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `df0e03c7c34eaaa3bc54d910927f65534fb7cdd82072c50f63264a9dd724a330`
