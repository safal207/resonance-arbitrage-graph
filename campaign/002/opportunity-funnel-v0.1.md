# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `545c812fc1e43ef3dda1898d0cf7d4e112fe4c5bde93d1a4ceb940b2f2d4e63c`
- Replay SHA-256: `520483ba1240f3b3921c4b6d64552ce47eb12c113e909b7f8e1cb1922eb8dd1a`

## Cumulative funnel

- Captured terminal cycles: **728**
- Complete evidence: **726** (99.73%)
- Structural constraints pass: **623** (85.58%)
- Gross-positive before costs: **108** (14.84%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -3.89 bps (min -35.06, max 8.52)**
- Expected net edge: **mean -39.83 bps (min -70.89, max -27.47)**
- Observed terminal edge: **mean -39.79 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.83, max 35.99)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 515 × `GROSS_NON_POSITIVE`
- 108 × `MODELED_COSTS_ERASE_EDGE`
- 57 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 24 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 22 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `a3dcfde0250bce2fd6cb7c04ca3863c8628c74cd6f4151d819463d759a41e470`
