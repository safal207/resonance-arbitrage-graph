# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `91763e290d4f079afa4646dd4ad2709e65dc1330c2efcf78aff43a24a939a319`
- Replay SHA-256: `eba90c0dfadae9f54b9272fee95b50726639dd78e2f480c12d78578c42d97baf`

## Cumulative funnel

- Captured terminal cycles: **390**
- Complete evidence: **388** (99.49%)
- Structural constraints pass: **341** (87.44%)
- Gross-positive before costs: **51** (13.08%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -4.02 bps (min -29.56, max 8.52)**
- Expected net edge: **mean -39.96 bps (min -65.41, max -27.47)**
- Observed terminal edge: **mean -39.97 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.85, max 35.99)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 290 × `GROSS_NON_POSITIVE`
- 51 × `MODELED_COSTS_ERASE_EDGE`
- 25 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 11 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 11 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `433c209fef6d6f1b931b632289abf84fe6c3436312ff2947495695f0784c957f`
