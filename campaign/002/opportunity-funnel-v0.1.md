# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `5a3940ab33c6ae387ad146b1826edb4f924686880cb557b9ff734752b7189fd7`
- Replay SHA-256: `9c00670e6e445c541013040f6c7bb040ce1f1e5599b175cd4d0a64ff7eb68256`

## Cumulative funnel

- Captured terminal cycles: **480**
- Complete evidence: **478** (99.58%)
- Structural constraints pass: **413** (86.04%)
- Gross-positive before costs: **66** (13.75%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -3.92 bps (min -29.56, max 8.52)**
- Expected net edge: **mean -39.86 bps (min -65.41, max -27.47)**
- Observed terminal edge: **mean -39.91 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.85, max 35.99)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 347 × `GROSS_NON_POSITIVE`
- 66 × `MODELED_COSTS_ERASE_EDGE`
- 32 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 18 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 15 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `cf42a5714215069ab88a7740667eb9ca5e09c77215967379194593b77d029ba7`
