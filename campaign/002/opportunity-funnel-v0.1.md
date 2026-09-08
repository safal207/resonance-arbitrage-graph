# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `9a400e9a200c31b36f8cb999ab825ea93e38b9214f3cf4c2d4492abd3a91f1bf`
- Replay SHA-256: `a86b3abeeb6151c2f39c6ba7a4bb3f1a0ef3ae9affc6720c50c69c1167082ecc`

## Cumulative funnel

- Captured terminal cycles: **700**
- Complete evidence: **698** (99.71%)
- Structural constraints pass: **601** (85.86%)
- Gross-positive before costs: **105** (15.00%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -3.86 bps (min -35.06, max 8.52)**
- Expected net edge: **mean -39.80 bps (min -70.89, max -27.47)**
- Observed terminal edge: **mean -39.77 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.83, max 35.99)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 496 × `GROSS_NON_POSITIVE`
- 105 × `MODELED_COSTS_ERASE_EDGE`
- 54 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 23 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 20 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `e1c9686d23ffa21224b0d67b97e88a1cacedda855be7008437bb7f634e8dfd08`
