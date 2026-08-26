# Product 0.1 — Opportunity Truth Benchmark Protocol

This document defines how RESONANCE Verify turns captured paper-market evidence into a product claim without mixing fixtures, future information or cherry-picked outcomes into the headline metric.

## Product hypothesis

A visible arbitrage signal often overstates executable opportunity quality.

RESONANCE Verify should create measurable value if its `EXECUTE_SIM` population has materially better later paper outcomes than the raw candidate population and if the system can explain why rejected/downgraded candidates failed.

The benchmark exists to test that hypothesis. It is not a profitability guarantee.

## Unit of analysis

The unit is one collapsed `logical_operation_id`, not one retry row.

```text
candidate detection
→ one decision identity
→ zero or more retries
→ one latest outcome state
→ one benchmark row
```

Retries therefore cannot inflate TP/FP counts.

## Evidence source classes

### Allowed for public product claims

- captured public real-market corpus;
- deterministic replay bundle exported from that corpus;
- later public outcome snapshots bound to the same logical operation.

### Not allowed for public product claims

- unit-test fixtures;
- synthetic cases;
- hand-edited replay rows;
- reports missing reproducible source evidence;
- exploratory threshold sweeps evaluated on the same outcomes used to select them.

Synthetic and fixture data remain valid for software testing, only not for marketing claims.

## Primary metrics

### Opportunity Truth Rate

```text
OTR = TRUE_POSITIVE / (TRUE_POSITIVE + FALSE_POSITIVE)
```

This answers: among determinate opportunities that the active deterministic policy allowed as `EXECUTE_SIM`, how often did the later observed edge still clear the required threshold?

### False Opportunity Rate

```text
FOR = FALSE_POSITIVE / (TRUE_POSITIVE + FALSE_POSITIVE)
```

### Route Survival Rate

```text
Route Survival = (TP + FP) / (TP + FP + EXPIRED)
```

Expiration is not silently folded into false positive because it is a different failure mode.

## Paper PnL metric

For an `EXECUTE_SIM` decision with a later observed edge:

```text
paper_pnl = start_amount * observed_edge_bps / 10_000
```

Aggregate paper PnL is calculated only for evaluated `EXECUTE_SIM` decisions with a realized edge. Rejected or observed candidates are not retroactively counted as if they had been executed.

The report also publishes evaluated capital so the PnL number cannot be read without its denominator.

## Sample-size gate

Default:

```text
min_truth_population = 30
```

where:

```text
truth_population = TP + FP
```

Below the gate, the report status is:

```text
INSUFFICIENT_TRUTH_POPULATION
```

At or above the gate:

```text
READY
```

`READY` means only that this explicit minimum sample-size guardrail passed. It does not establish statistical significance, economic profitability or future performance.

## Required segmentation

The report preserves:

- overall metrics;
- market-regime slices;
- semantic route slices;
- downgrade/rejection reason counts.

A strong overall number must not hide one route or regime that performs badly.

## Claim ladder

Product messaging should mature in this order.

### Level 0 — capability claim

> RESONANCE Verify checks whether a candidate route still satisfies explicit execution constraints and emits deterministic evidence.

This is supported by software behavior and tests.

### Level 1 — benchmark-process claim

> RESONANCE measures later TP/FP/expired outcomes on a hash-bound public-market corpus.

This is supported once the real-market capture and benchmark pipeline is running.

### Level 2 — measured product claim

Example form only:

> Across N determinate `EXECUTE_SIM` outcomes in corpus SHA X, Opportunity Truth Rate was Y%.

This may be published only when the exact number is generated from the real-market corpus and the report is reproducible.

### Level 3 — comparative claim

Example:

> RESONANCE reduced false opportunities versus baseline scanner B by X%.

This requires a separately defined baseline evaluated on the same chronological corpus. Product 0.1 does not invent this baseline.

## Design-partner question

The first outreach should start with the operational problem, not the architecture:

> **When your trading agent sees an opportunity, how do you verify it is still executable before letting it act?**

Follow-up discovery should identify:

- what produces the candidate;
- what currently sits between signal and execution;
- which false-positive modes cost the most time or money;
- whether they need a synchronous verifier, offline replay, or both;
- which evidence they need for incident review or governance;
- what latency budget a verifier must meet.

Do not lead with policy lineage, hash chains or ML unless the customer pulls the conversation there.

## Product success criteria

Product 0.1 is successful when all of the following are true:

1. a new visitor understands the problem and verdict in under 30 seconds;
2. a real-market corpus can be turned into a deterministic benchmark report with one command;
3. the report refuses to imply readiness below its sample-size gate;
4. at least one design partner confirms the signal-to-execution verification gap is real;
5. the next engineering investment is selected from observed customer demand rather than version sequence.
