# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `034ab7a6879c3e9a1cbe3a3c9062273834d83b038a2db2002483757ceb0c2eb0`
- Replay SHA-256: `2274caf7540944c047a8ddb330e246ffa1a410bca45eb4fef259d14bad35fb99`

## Cumulative funnel

- Captured terminal cycles: **858**
- Complete evidence: **856** (99.77%)
- Structural constraints pass: **727** (84.73%)
- Gross-positive before costs: **126** (14.69%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -3.92 bps (min -35.06, max 8.52)**
- Expected net edge: **mean -39.86 bps (min -70.89, max -27.47)**
- Observed terminal edge: **mean -39.82 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.83, max 35.99)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 601 × `GROSS_NON_POSITIVE`
- 126 × `MODELED_COSTS_ERASE_EDGE`
- 78 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 27 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 24 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `153f5acc703d9cd6cc5156ea876cacc4532d159a019319578e85cf05bfd4fa93`
