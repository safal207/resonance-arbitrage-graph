# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `951ce14657cbe751a93ca06da6943768c509ea2f8836e331b5b1cd308f6f5651`
- Replay SHA-256: `34755a61c0abedee0e5a395cbc214551d281e300f7789bef309171ebbb1b7978`

## Cumulative funnel

- Captured terminal cycles: **650**
- Complete evidence: **648** (99.69%)
- Structural constraints pass: **562** (86.46%)
- Gross-positive before costs: **102** (15.69%)
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

- 460 × `GROSS_NON_POSITIVE`
- 102 × `MODELED_COSTS_ERASE_EDGE`
- 44 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 23 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 19 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `fb495836cf4d2f81281a3fa4e26d34358eabaddbada4b50cdc0498cfecc1b33a`
