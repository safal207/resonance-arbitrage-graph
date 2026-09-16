# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `5f172ac100f29f3812a65dae56053d9713bda1a8ba305c49394d74b0bd1eb014`
- Replay SHA-256: `ab4a11eb47eb4cf4dab3ab1ab284cd18cf4d33ffc4f6b1955d10d74c904bd38f`

## Cumulative funnel

- Captured terminal cycles: **1250**
- Complete evidence: **1248** (99.84%)
- Structural constraints pass: **1033** (82.64%)
- Gross-positive before costs: **172** (13.76%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -3.99 bps (min -35.06, max 8.52)**
- Expected net edge: **mean -39.93 bps (min -70.89, max -27.47)**
- Observed terminal edge: **mean -39.85 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.83, max 35.99)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 861 × `GROSS_NON_POSITIVE`
- 172 × `MODELED_COSTS_ERASE_EDGE`
- 128 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 48 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 39 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `d531769ed6fb65e5f7264afdc4b0e113e678ca1faefd081358fe4bd49ce8fa5c`
