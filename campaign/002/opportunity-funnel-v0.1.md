# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `d29889ff3c327cf3a64baafd4517de506c9d53a98752e83006bfd329f107d5e0`
- Replay SHA-256: `f04428acf337749056b4634dc205064d8a910254dfee5745311086d789800dd4`

## Cumulative funnel

- Captured terminal cycles: **660**
- Complete evidence: **658** (99.70%)
- Structural constraints pass: **570** (86.36%)
- Gross-positive before costs: **103** (15.61%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -3.88 bps (min -35.06, max 8.52)**
- Expected net edge: **mean -39.83 bps (min -70.89, max -27.47)**
- Observed terminal edge: **mean -39.78 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.83, max 35.99)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 467 × `GROSS_NON_POSITIVE`
- 103 × `MODELED_COSTS_ERASE_EDGE`
- 46 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 23 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 19 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `6249dc475da49c557a50112cfabeb932ec9a97e0f6f9be82fee31777ee36952b`
