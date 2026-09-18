# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `e5c52fcb47eee14b5e4d6e6c779695cd059bafdd3b1a0836cd4a5be77284f7ce`
- Replay SHA-256: `5b4075ed41dbd584cc557bd81abd0bb09abfb02c094fd9a33bb43fa43a7e604c`

## Cumulative funnel

- Captured terminal cycles: **1360**
- Complete evidence: **1358** (99.85%)
- Structural constraints pass: **1128** (82.94%)
- Gross-positive before costs: **182** (13.38%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -4.08 bps (min -40.61, max 10.88)**
- Expected net edge: **mean -40.02 bps (min -76.42, max -25.12)**
- Observed terminal edge: **mean -39.94 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.81, max 36.00)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 946 × `GROSS_NON_POSITIVE`
- 182 × `MODELED_COSTS_ERASE_EDGE`
- 134 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 51 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 45 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `91cdbd6f15839b35b11d720702351da17ba77e3faa2b6a8a27fd8f633b787a2c`
