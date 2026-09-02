# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `2bf908dc8e20e7c106d2ce2c941dd357aec3fca20b0a7cd6355eda62a99e0e72`
- Replay SHA-256: `95b6f9f698bb628f27b6c22cc61dfb679d10c73e0e7d61671f1175b1ec790b0a`

## Cumulative funnel

- Captured terminal cycles: **260**
- Complete evidence: **260** (100.00%)
- Structural constraints pass: **231** (88.85%)
- Gross-positive before costs: **37** (14.23%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -4.18 bps (min -29.56, max 5.22)**
- Expected net edge: **mean -40.12 bps (min -65.41, max -30.75)**
- Observed terminal edge: **mean -40.10 bps (min -88.73, max -30.64)**
- Modeled cost drag: **mean 35.94 bps (min 35.85, max 35.98)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 194 × `GROSS_NON_POSITIVE`
- 37 × `MODELED_COSTS_ERASE_EDGE`
- 12 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 9 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 8 × `STRUCTURAL:CAPACITY_EXCEEDED:0`

Evidence SHA-256: `9d88b0119a1c3dd964a6220b25a7a7948dc0fe12e2c4b9c862076fc3978cd870`
