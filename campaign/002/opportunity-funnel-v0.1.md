# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `ba7fabad37953f71680212a77773633161dffaacd6b5b3841a5321b68bfccf87`
- Replay SHA-256: `ac6563723c8208146b5e20660619ed1b1073f8ccd3c880f03a95683393750b7a`

## Cumulative funnel

- Captured terminal cycles: **470**
- Complete evidence: **468** (99.57%)
- Structural constraints pass: **406** (86.38%)
- Gross-positive before costs: **64** (13.62%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -3.93 bps (min -29.56, max 8.52)**
- Expected net edge: **mean -39.87 bps (min -65.41, max -27.47)**
- Observed terminal edge: **mean -39.88 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.85, max 35.99)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 342 × `GROSS_NON_POSITIVE`
- 64 × `MODELED_COSTS_ERASE_EDGE`
- 31 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 16 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 15 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `bfadb6008b75a0e106c5afcd4a0ea52aad3ba15ef427b59197f122ae07d45e32`
