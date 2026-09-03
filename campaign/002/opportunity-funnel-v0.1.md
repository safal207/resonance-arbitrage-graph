# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `fd8fa080b2f4c1bd2a39ab6db778e391769d6577cdc6a818d36fc42ef7cd3807`
- Replay SHA-256: `4681230ce628d0d1e01d10bf5d46716adceee2b1ead72ded0c5579b32e8d12fa`

## Cumulative funnel

- Captured terminal cycles: **350**
- Complete evidence: **348** (99.43%)
- Structural constraints pass: **306** (87.43%)
- Gross-positive before costs: **45** (12.86%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -4.10 bps (min -29.56, max 8.52)**
- Expected net edge: **mean -40.05 bps (min -65.41, max -27.47)**
- Observed terminal edge: **mean -40.03 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.85, max 35.99)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 261 × `GROSS_NON_POSITIVE`
- 45 × `MODELED_COSTS_ERASE_EDGE`
- 20 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 11 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 11 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `245b2060d020d92f71b9b246db4068766e94d2aeab84811af8675e1bda1eb74d`
