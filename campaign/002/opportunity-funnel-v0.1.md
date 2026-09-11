# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `973b2bff5382319bff07d7d954777f19ff16b4a6b1d4e1b17a177134e2e8c5b9`
- Replay SHA-256: `63c1c7a719ed38043e76c0bfd656240db87a5f11c5322f19fdb42397efaeccc4`

## Cumulative funnel

- Captured terminal cycles: **888**
- Complete evidence: **886** (99.77%)
- Structural constraints pass: **752** (84.68%)
- Gross-positive before costs: **129** (14.53%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -3.94 bps (min -35.06, max 8.52)**
- Expected net edge: **mean -39.88 bps (min -70.89, max -27.47)**
- Observed terminal edge: **mean -39.82 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.83, max 35.99)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 623 × `GROSS_NON_POSITIVE`
- 129 × `MODELED_COSTS_ERASE_EDGE`
- 83 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 27 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 24 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `93a7da06eda3f38df521d05ba5936c5ea41a5232e18c22492c0de4f4934c8e09`
