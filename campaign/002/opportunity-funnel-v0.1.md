# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `ef5e3a122782cd546b25271fde638573716eadfdaacdd1429a3d7565200e1b0a`
- Replay SHA-256: `a691290ac62648e2786edc71d0143773a70a8a1e7cf127af4d53a47cd1d64638`

## Cumulative funnel

- Captured terminal cycles: **680**
- Complete evidence: **678** (99.71%)
- Structural constraints pass: **588** (86.47%)
- Gross-positive before costs: **104** (15.29%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -3.86 bps (min -35.06, max 8.52)**
- Expected net edge: **mean -39.81 bps (min -70.89, max -27.47)**
- Observed terminal edge: **mean -39.76 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.83, max 35.99)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 484 × `GROSS_NON_POSITIVE`
- 104 × `MODELED_COSTS_ERASE_EDGE`
- 47 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 23 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 20 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `ac6489f8002ee5e6468c7e71360051105a0f76bd372a2607aeefa71f05e08a78`
