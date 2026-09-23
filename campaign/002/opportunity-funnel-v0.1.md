# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `edf94a597644e0ad60fc0098acc10ce1074da90bb71f41468df04fb562f20cfc`
- Replay SHA-256: `bb69e3ec7c1d022492ad23550d77b6ece234061e60cd3f7bae30bb83ea2b4875`

## Cumulative funnel

- Captured terminal cycles: **1700**
- Complete evidence: **1696** (99.76%)
- Structural constraints pass: **1414** (83.18%)
- Gross-positive before costs: **210** (12.35%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -4.23 bps (min -40.61, max 10.88)**
- Expected net edge: **mean -40.18 bps (min -76.42, max -25.12)**
- Observed terminal edge: **mean -40.10 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.81, max 36.00)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 1204 × `GROSS_NON_POSITIVE`
- 210 × `MODELED_COSTS_ERASE_EDGE`
- 162 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 61 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 59 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 4 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `95104506ee885797db7b57cbd21619257b65362b87105fe7170627fcf049080b`
