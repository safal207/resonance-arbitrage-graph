# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `28829310e35da37b61cf7eb8ae7ed3e4581967ad57d8907ef5de59f5e0263f22`
- Replay SHA-256: `cd2eb6b98a955710408ed43c07a155d843b16e5e276c3e51537b14062cf758f3`

## Cumulative funnel

- Captured terminal cycles: **1050**
- Complete evidence: **1048** (99.81%)
- Structural constraints pass: **883** (84.10%)
- Gross-positive before costs: **155** (14.76%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -3.92 bps (min -35.06, max 8.52)**
- Expected net edge: **mean -39.86 bps (min -70.89, max -27.47)**
- Observed terminal edge: **mean -39.80 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.83, max 35.99)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 728 × `GROSS_NON_POSITIVE`
- 155 × `MODELED_COSTS_ERASE_EDGE`
- 103 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 33 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 29 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `190f162b1e9993fce82cd9fcbf7e0625de80937fe2f3601b06e272782da410f8`
