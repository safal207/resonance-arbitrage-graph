# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `94b0479a05d7a08de33ac6be34035f7d4352eca607782fa8bdb4a0a5c75a10c9`
- Replay SHA-256: `ff08c0cd2e53839d9b64e98524a61af1d5c94481d74c00d2bc8692fb42f5ddbc`

## Cumulative funnel

- Captured terminal cycles: **200**
- Complete evidence: **200** (100.00%)
- Structural constraints pass: **177** (88.50%)
- Gross-positive before costs: **28** (14.00%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -4.20 bps (min -29.56, max 5.22)**
- Expected net edge: **mean -40.14 bps (min -65.41, max -30.75)**
- Observed terminal edge: **mean -40.20 bps (min -88.73, max -30.80)**
- Modeled cost drag: **mean 35.94 bps (min 35.85, max 35.98)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 149 × `GROSS_NON_POSITIVE`
- 28 × `MODELED_COSTS_ERASE_EDGE`
- 10 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 7 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 6 × `STRUCTURAL:CAPACITY_EXCEEDED:0`

Evidence SHA-256: `768181729bed9653ccfae5a6f4e9c75ea7473fa68c284a29c8f60dff3c5abb30`
