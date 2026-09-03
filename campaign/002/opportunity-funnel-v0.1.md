# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `2330befe2c3ec6123858f5f43fd0b47f08ad10ed44ba73947eb0fd1ba97ddca2`
- Replay SHA-256: `c286759a0910b5a8ae5129ef3498ebe351ed69f26ed3bd1db3df9087eb6bebb4`

## Cumulative funnel

- Captured terminal cycles: **340**
- Complete evidence: **338** (99.41%)
- Structural constraints pass: **297** (87.35%)
- Gross-positive before costs: **44** (12.94%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -4.11 bps (min -29.56, max 8.52)**
- Expected net edge: **mean -40.05 bps (min -65.41, max -27.47)**
- Observed terminal edge: **mean -40.04 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.85, max 35.99)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 253 × `GROSS_NON_POSITIVE`
- 44 × `MODELED_COSTS_ERASE_EDGE`
- 19 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 11 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 11 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `f6b3b2c2cfede305abb49a52f3856af949307a920bc7de10d1e1a4da48825341`
