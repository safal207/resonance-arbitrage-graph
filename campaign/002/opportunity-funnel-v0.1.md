# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `77a50bd1e6c1ab948d6a8eca24a224bea6cbe4e6263ca9b02aa57f8dd9001ff2`
- Replay SHA-256: `a545f935b7c238b196da12fb73597fe74c5bafdec5929d0e9e192802f989a342`

## Cumulative funnel

- Captured terminal cycles: **1790**
- Complete evidence: **1786** (99.78%)
- Structural constraints pass: **1483** (82.85%)
- Gross-positive before costs: **214** (11.96%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -4.25 bps (min -40.61, max 10.88)**
- Expected net edge: **mean -40.19 bps (min -76.42, max -25.12)**
- Observed terminal edge: **mean -40.11 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.81, max 36.00)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 1269 × `GROSS_NON_POSITIVE`
- 214 × `MODELED_COSTS_ERASE_EDGE`
- 174 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 65 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 64 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 4 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `24a3b3ef7e2790adfab4b244a6e639e96758d05a9e054b15c5bcb7286800a81e`
