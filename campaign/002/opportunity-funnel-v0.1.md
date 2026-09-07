# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `5aa89d5b7825924ce606a16efc7ee64665a346669dd899d15a65be47a22cdf06`
- Replay SHA-256: `738194527e18aca292fa7308ff4a52407bc1f3e26758c2bfed78addb139326c3`

## Cumulative funnel

- Captured terminal cycles: **670**
- Complete evidence: **668** (99.70%)
- Structural constraints pass: **579** (86.42%)
- Gross-positive before costs: **104** (15.52%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -3.87 bps (min -35.06, max 8.52)**
- Expected net edge: **mean -39.82 bps (min -70.89, max -27.47)**
- Observed terminal edge: **mean -39.77 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.83, max 35.99)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 475 × `GROSS_NON_POSITIVE`
- 104 × `MODELED_COSTS_ERASE_EDGE`
- 47 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 23 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 19 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `4c2f7e97991ee0e898c93e069fc1fc5e7e4c038b6d14cfd1b417528d4055aaa3`
