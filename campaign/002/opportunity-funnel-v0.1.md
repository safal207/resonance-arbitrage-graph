# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `8572ec1494473fcd95970b5e7b76df8f57d167a0d1de2a6b806b634e69033fea`
- Replay SHA-256: `c5def5da07e0c3ddbd4748b447f78fd0c6ead4f3d7912317aa1f3b294dc37c1b`

## Cumulative funnel

- Captured terminal cycles: **1390**
- Complete evidence: **1388** (99.86%)
- Structural constraints pass: **1153** (82.95%)
- Gross-positive before costs: **184** (13.24%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -4.09 bps (min -40.61, max 10.88)**
- Expected net edge: **mean -40.03 bps (min -76.42, max -25.12)**
- Observed terminal edge: **mean -39.94 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.81, max 36.00)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 969 × `GROSS_NON_POSITIVE`
- 184 × `MODELED_COSTS_ERASE_EDGE`
- 135 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 53 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 47 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `af35fb612cf89043c3163a6009fb503c12ab7ae8ab51ccc30bf0fbf3b5bf59f9`
