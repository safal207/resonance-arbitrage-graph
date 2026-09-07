# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `394db13bc84db5579310fc12ca23c8b035280f4788a9ac82270d45bf381b5000`
- Replay SHA-256: `7a8ea212afa54156bb1495f4ad7039ee0040e02b97f12d4c2573e336fa3631cc`

## Cumulative funnel

- Captured terminal cycles: **630**
- Complete evidence: **628** (99.68%)
- Structural constraints pass: **543** (86.19%)
- Gross-positive before costs: **94** (14.92%)
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

- 449 × `GROSS_NON_POSITIVE`
- 94 × `MODELED_COSTS_ERASE_EDGE`
- 44 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 23 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 18 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `140bfb2b13f2a8fe57b540653868a45d5c90370e3ecf6f6b311ca31cfc9ea221`
