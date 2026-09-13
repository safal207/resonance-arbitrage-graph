# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `f5444253ee9f6b0eca84f465c49304faa6704ddc6f821c1df64186a5b62d72de`
- Replay SHA-256: `64a3367cb77d83e911a9347069a03cd35e8bc2024fb2cb30f4365915094e5f05`

## Cumulative funnel

- Captured terminal cycles: **1020**
- Complete evidence: **1018** (99.80%)
- Structural constraints pass: **856** (83.92%)
- Gross-positive before costs: **149** (14.61%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -3.91 bps (min -35.06, max 8.52)**
- Expected net edge: **mean -39.86 bps (min -70.89, max -27.47)**
- Observed terminal edge: **mean -39.80 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.83, max 35.99)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 707 × `GROSS_NON_POSITIVE`
- 149 × `MODELED_COSTS_ERASE_EDGE`
- 100 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 33 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 29 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `231c008a961b3316787d2117a79c3c0d96c1910e47392948af18b02fa8b99dbb`
