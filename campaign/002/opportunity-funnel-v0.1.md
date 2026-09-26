# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `02bc2fec21462787fd0686f3504bef4087981bc3add787a2430dbb3ef516b028`
- Replay SHA-256: `8d13cc5690b0787fcc266141e34390b8d793ecc18e8cb6b71fc5a86963b1a108`

## Cumulative funnel

- Captured terminal cycles: **1840**
- Complete evidence: **1836** (99.78%)
- Structural constraints pass: **1525** (82.88%)
- Gross-positive before costs: **218** (11.85%)
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

- 1307 × `GROSS_NON_POSITIVE`
- 218 × `MODELED_COSTS_ERASE_EDGE`
- 179 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 67 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 65 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 4 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `53f40c6c578584aaca143d8376c7d41a53df5e19fc5a6e48d001e7756f294a1c`
