# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `2536290a39375b6f786daa7a1c05075bcdab18dc534170f1dd12e0caf79a61a2`
- Replay SHA-256: `5c4279fb9119b286b1e9a5f925817c6e48c5ad32bf66efb5e3b6a34daac07dec`

## Cumulative funnel

- Captured terminal cycles: **250**
- Complete evidence: **250** (100.00%)
- Structural constraints pass: **221** (88.40%)
- Gross-positive before costs: **36** (14.40%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -4.20 bps (min -29.56, max 5.22)**
- Expected net edge: **mean -40.15 bps (min -65.41, max -30.75)**
- Observed terminal edge: **mean -40.13 bps (min -88.73, max -30.64)**
- Modeled cost drag: **mean 35.94 bps (min 35.85, max 35.98)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 185 × `GROSS_NON_POSITIVE`
- 36 × `MODELED_COSTS_ERASE_EDGE`
- 12 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 9 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 8 × `STRUCTURAL:CAPACITY_EXCEEDED:0`

Evidence SHA-256: `a88795a69bca2d38b322dad7d0039835e81dd291f8e19704e4f69fcb75f9c43d`
