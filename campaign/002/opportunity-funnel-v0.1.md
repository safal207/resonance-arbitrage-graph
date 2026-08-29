# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `2729f27be704b20fee0b2633a149d94e864a8efce68bf4604b34015ded7dd0db`
- Replay SHA-256: `2cd4b3fbbb0a8dc05f63e394d4f4e47fc0b227e97195760d4f3dfe8d34103ecc`

## Cumulative funnel

- Captured terminal cycles: **40**
- Complete evidence: **40** (100.00%)
- Structural constraints pass: **37** (92.50%)
- Gross-positive before costs: **6** (15.00%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -4.28 bps (min -19.95, max 3.25)**
- Expected net edge: **mean -40.23 bps (min -55.84, max -32.72)**
- Observed terminal edge: **mean -40.12 bps (min -57.05, max -30.80)**
- Modeled cost drag: **mean 35.94 bps (min 35.89, max 35.97)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 31 × `GROSS_NON_POSITIVE`
- 6 × `MODELED_COSTS_ERASE_EDGE`
- 2 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 1 × `STRUCTURAL:CAPACITY_EXCEEDED:2`

Evidence SHA-256: `a4dd83756786b2e5fd5b4c57f5df249e08ba713ca5fa365c50c36e9123acfba0`
