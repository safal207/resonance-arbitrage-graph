# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `68e61cf8c43c7ebe3640033416ddbb532209c25d9acdb69aba288c6e236102be`
- Replay SHA-256: `f70351af72d867340dcdfb898acfd4c3fd49fc0b305a7f73c938faec23f0468f`

## Cumulative funnel

- Captured terminal cycles: **180**
- Complete evidence: **180** (100.00%)
- Structural constraints pass: **162** (90.00%)
- Gross-positive before costs: **25** (13.89%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -4.27 bps (min -29.56, max 5.22)**
- Expected net edge: **mean -40.21 bps (min -65.41, max -30.75)**
- Observed terminal edge: **mean -40.29 bps (min -88.73, max -30.80)**
- Modeled cost drag: **mean 35.94 bps (min 35.85, max 35.98)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 137 × `GROSS_NON_POSITIVE`
- 25 × `MODELED_COSTS_ERASE_EDGE`
- 9 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 6 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 3 × `STRUCTURAL:CAPACITY_EXCEEDED:0`

Evidence SHA-256: `591929a2c97aea08ef5e1bff67536db881a0f97aa5aaffac6a394149509895ac`
