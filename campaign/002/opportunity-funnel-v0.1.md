# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `91b4f10c366891d6cdd49ef807edc00459958564b5d6331615c3bdfe3a39c690`
- Replay SHA-256: `f4a75180240dc71a399a98978fc2fa58e56cb439ebeb290610fd45c2eca0dafb`

## Cumulative funnel

- Captured terminal cycles: **1640**
- Complete evidence: **1636** (99.76%)
- Structural constraints pass: **1363** (83.11%)
- Gross-positive before costs: **203** (12.38%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -4.23 bps (min -40.61, max 10.88)**
- Expected net edge: **mean -40.17 bps (min -76.42, max -25.12)**
- Observed terminal edge: **mean -40.10 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.81, max 36.00)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 1160 × `GROSS_NON_POSITIVE`
- 203 × `MODELED_COSTS_ERASE_EDGE`
- 159 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 58 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 56 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 4 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `5f005d98324b0be9ee7bd8bde8e40d1bfbd63cb6a37f6307a2834ab9d635f8fc`
