# RESONANCE Verify — Opportunity Funnel Benchmark

- Evidence source: **REAL_MARKET_CORPUS**
- Source SHA-256: `71468aa345227890b3ec900ddd389b433746a85655934d6ec66b00705f21c265`
- Replay SHA-256: `bfac8f204d299533f848d529cf406336d340d19e2f070185d8f10632525ab8de`

## Cumulative funnel

- Captured terminal cycles: **430**
- Complete evidence: **428** (99.53%)
- Structural constraints pass: **372** (86.51%)
- Gross-positive before costs: **55** (12.79%)
- Net-positive after modeled costs: **0** (0.00%)
- Execute-threshold eligible: **0** (0.00%)
- Final EXECUTE_SIM: **0** (0.00%)
- Resolved execute outcomes: **0** (0.00%)
- TP + FP truth outcomes: **0** (0.00%)
- Survived required edge: **0** (0.00%)

## Edge distributions

- Gross edge: **mean -3.99 bps (min -29.56, max 8.52)**
- Expected net edge: **mean -39.93 bps (min -65.41, max -27.47)**
- Observed terminal edge: **mean -39.95 bps (min -88.73, max -26.12)**
- Modeled cost drag: **mean 35.94 bps (min 35.85, max 35.99)**

## Interpretation boundary

Gross-positive is not a trading instruction. Rejected routes are not false positives. An empty downstream stage is valid evidence that no candidate crossed the bound verification policy.

**OTR is unavailable, not zero:** no candidate entered `EXECUTE_SIM`, so there is no truth denominator to grade.

## First blocker

- 317 × `GROSS_NON_POSITIVE`
- 55 × `MODELED_COSTS_ERASE_EDGE`
- 29 × `STRUCTURAL:CAPACITY_EXCEEDED:1`
- 14 × `STRUCTURAL:CAPACITY_EXCEEDED:2`
- 13 × `STRUCTURAL:CAPACITY_EXCEEDED:0`
- 2 × `INCOMPLETE_EVIDENCE`

Evidence SHA-256: `1a3fbcb1392d0bd8e1d95eef44f6aa3918f06f1fe746a166efa61715b8669326`
