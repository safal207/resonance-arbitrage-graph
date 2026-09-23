# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `4453ad1e505c01a372104e631c283fca85f43f3745292926cad0607dc2d5cdf0`
- Replay SHA-256: `c6a358ae270727481e9272d34bc6959e0ee0fa84e1d3241d9030e6882e0b1316`

## Cumulative funnel

- Captured terminal cycles: **1660**
- Complete evidence: **1656** (99.76%)
- Structural constraints pass: **1379** (83.07%)
- Gross-positive before costs: **205** (12.35%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -4.23 bps (min -40.61, max 10.88)**
- Expected net edge: **mean -40.17 bps (min -76.42, max -25.12)**
- Observed terminal edge: **mean -40.10 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.81, max 36.00)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 1174 × `GROSS_NON_POSITIVE`
- 205 × `MODELED_COSTS_ERASE_EDGE`
- 159 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 61 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 57 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 4 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `b07fddadb38241afb6adf9a89b219c700c9590f75878ec1073ff3caf1630c21c`
