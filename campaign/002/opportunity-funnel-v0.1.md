# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `2f406af3f999e75f2e08bbcdb49cddc9031221197c61a197a203a31b5237aa77`
- Replay SHA-256: `43a25425aac0474e1d3b0de49e1edf644fb0e17072aa11d8bfb3608cabd1d25c`

## Cumulative funnel

- Captured terminal cycles: **1510**
- Complete evidence: **1508** (99.87%)
- Structural constraints pass: **1255** (83.11%)
- Gross-positive before costs: **192** (12.72%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -4.18 bps (min -40.61, max 10.88)**
- Expected net edge: **mean -40.12 bps (min -76.42, max -25.12)**
- Observed terminal edge: **mean -40.04 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.81, max 36.00)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 1063 × `GROSS_NON_POSITIVE`
- 192 × `MODELED_COSTS_ERASE_EDGE`
- 149 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 54 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 50 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `b3a4d7cd46cdf7b53668905b171f919fc44e5716563085aae09f87a6616d9a57`
