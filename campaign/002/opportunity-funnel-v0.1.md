# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `a84549ae8666d05de50eced741e3b4a905348db4e034c892fd1b05e1c352f54f`
- Replay SHA-256: `9eb47990fd016ade057e81c8bc5cb51d59cbaaf634d0b9fbae97e04d6875dd60`

## Cumulative funnel

- Captured terminal cycles: **530**
- Complete evidence: **528** (99.62%)
- Structural constraints pass: **458** (86.42%)
- Gross-positive before costs: **76** (14.34%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -3.91 bps (min -35.06, max 8.52)**
- Expected net edge: **mean -39.86 bps (min -70.89, max -27.47)**
- Observed terminal edge: **mean -39.85 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.83, max 35.99)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 382 × `GROSS_NON_POSITIVE`
- 76 × `MODELED_COSTS_ERASE_EDGE`
- 36 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 18 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 16 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `21c6317e0ff42a57fee0347ec64da72c3a94c50bbe03a1c0d9ec129f614a43b2`
