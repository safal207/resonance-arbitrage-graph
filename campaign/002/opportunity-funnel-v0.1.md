# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `40afee7778370f23ca9b6ce9ba6e7d3476449c4830781a73520850c2027114ba`
- Replay SHA-256: `b5b2329b092de07d3508363ad6f777140a871c717c9b04d860943bf94b2ab722`

## Cumulative funnel

- Captured terminal cycles: **818**
- Complete evidence: **816** (99.76%)
- Structural constraints pass: **691** (84.47%)
- Gross-positive before costs: **122** (14.91%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -3.90 bps (min -35.06, max 8.52)**
- Expected net edge: **mean -39.84 bps (min -70.89, max -27.47)**
- Observed terminal edge: **mean -39.81 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.83, max 35.99)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 569 × `GROSS_NON_POSITIVE`
- 122 × `MODELED_COSTS_ERASE_EDGE`
- 74 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 27 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 24 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `e1e92f268056862671f7adbc5ce1ba139919c01d1a66892617cb5d828fa0e801`
