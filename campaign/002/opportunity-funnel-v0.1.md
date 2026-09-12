# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `8c79c3cb8e6b21ac31ab937be505e94dac28d4b0b6fbfbf3c9cb763a2e4daca7`
- Replay SHA-256: `dcc937266b341c28e95c07db0f081e3d2183887dfd5e2b739ea05e5c1b0ba8b7`

## Cumulative funnel

- Captured terminal cycles: **990**
- Complete evidence: **988** (99.80%)
- Structural constraints pass: **836** (84.44%)
- Gross-positive before costs: **148** (14.95%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -3.94 bps (min -35.06, max 8.52)**
- Expected net edge: **mean -39.88 bps (min -70.89, max -27.47)**
- Observed terminal edge: **mean -39.82 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.83, max 35.99)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 688 × `GROSS_NON_POSITIVE`
- 148 × `MODELED_COSTS_ERASE_EDGE`
- 94 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 31 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 27 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `9a643c67a8f61fca7fed297e44a005f85f5a4245e54ae951e83b8c9c98ad69fc`
