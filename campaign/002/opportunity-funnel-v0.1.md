# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `6142fd9581901f4731c924c82903fa80370e92c46dc6e68f9c4065fb8fcaba62`
- Replay SHA-256: `07d4873ac0c277cb4eee4a64e8ef9d9814718d9f5900b1e49661c0a45f34ce78`

## Cumulative funnel

- Captured terminal cycles: **270**
- Complete evidence: **270** (100.00%)
- Structural constraints pass: **241** (89.26%)
- Gross-positive before costs: **37** (13.70%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -4.19 bps (min -29.56, max 5.22)**
- Expected net edge: **mean -40.13 bps (min -65.41, max -30.75)**
- Observed terminal edge: **mean -40.10 bps (min -88.73, max -30.64)**
- Modeled cost drag: **mean 35.94 bps (min 35.85, max 35.98)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 204 × `GROSS_NON_POSITIVE`
- 37 × `MODELED_COSTS_ERASE_EDGE`
- 12 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 9 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 8 × `STRUCTURAL:CAPACITY_EXCEEDED:0`

Evidence SHA-256: `2ed2016ec4235e208d7bae26a84af8649ff88e5589a069fadc1c614bcdb71775`
