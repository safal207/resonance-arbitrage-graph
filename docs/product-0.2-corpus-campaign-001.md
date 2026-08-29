# Product 0.2 — Corpus Campaign 001

## Product objective

Produce the first reproducible RESONANCE Verify Opportunity Truth Benchmark from captured public real-market evidence.

This campaign is a data/proof operation, not a new trading strategy and not a live-execution rollout.

```text
public market decision state
→ deterministic RESONANCE verdict
→ persist decision before waiting
→ minimum outcome horizon
→ later public quote capture
→ paper outcome
→ append-only corpus
→ corpus-quality gate
→ Opportunity Truth Benchmark v0.2
```

## Why the campaign runner is resumable

The existing one-shot runner intentionally persists the decision before the outcome horizon. That preserves the anti-lookahead boundary, but a process interruption can leave a valid pending decision.

`resonance-corpus-campaign-step` adds a narrow recovery layer:

1. load and verify the current corpus;
2. find matured pending cases for the exact venue and market set;
3. obtain a fresh public quote set;
4. recompute and append their outcomes;
5. verify the persisted corpus hash;
6. only then start the next one-shot capture.

Recovery never changes the original decision state. It appends a later attempt under the same `logical_operation_id`.

A pending case from another venue or market set is not touched. A quote observed before the configured horizon is rejected.

## Campaign 001 frozen assumptions

The scheduled workflow uses Kraken public PreTrade data and several USD/BTC triangular market sets.

Paper-model assumptions are explicit and frozen in the workflow:

```text
start state:               KRAKEN_SPOT:USD
normal amount:             1,000 USD units
capacity-stress amount:    250,000 USD units
fee assumption:            10 bps per leg
slippage assumption:        2 bps per leg
minimum net EXECUTE_SIM:    5 bps
minimum outcome horizon:   60 seconds
rolling samples:            5
```

These are experiment assumptions. They are not a claim about a user's Kraken fee tier, guaranteed slippage, fill quality or achievable live execution.

Market profiles:

- BTC/USD + ETH/BTC + ETH/USD;
- BTC/USD + SOL/BTC + SOL/USD;
- BTC/USD + ADA/BTC + ADA/USD;
- BTC/USD + XRP/BTC + XRP/USD;
- BTC/USD + LTC/BTC + LTC/USD;
- ADA capacity-stress profile using the same frozen decision policy.

The capacity-stress profile exists to exercise the evidence-derived liquidity regime. It does not count as live capital deployment.

## Persistence model

Code lives on `main`.

Campaign evidence is committed to the dedicated branch:

```text
data/corpus-campaign-001
```

Expected paths:

```text
campaign/001/corpus.json
campaign/001/replay.json
campaign/001/opportunity-truth-v0.2.json
campaign/001/opportunity-truth-v0.2.md
campaign/001/receipts/<workflow-run>/<profile>.json
campaign/001/logs/<workflow-run>/<profile>.log
```

The corpus itself is append-only and hash-chained. Workflow commits are a transport/history layer, not the source of causal validity.

## Readiness gate

The benchmark remains `NOT_READY` until all bound gates pass.

Default quantity gates:

```text
terminal operations >= 100
determinate truth events >= 30
```

Default corpus-quality gates:

```text
distinct decision batches >= 20
effective decision batches >= 10
temporal span >= 1 hour
distinct route topologies >= 3
effective routes >= 2
distinct route markets >= 3
distinct regimes >= 2
```

Passing these gates produces `INTERNAL_EVIDENCE_READY`, not publication approval and not proof of profitability.

## Scheduled operation

`.github/workflows/corpus-campaign-001.yml` runs twice per hour and can also be started manually.

Each profile failure is isolated and logged. Successful profiles still advance the corpus. The workflow fails only when no profile completes, preventing silent zero-progress runs.

After the profile steps, the workflow:

1. builds Opportunity Truth Benchmark v0.2;
2. performs full source-bound verification;
3. commits updated evidence to the data branch;
4. uploads the same evidence as a workflow artifact.

## Claim boundary

A future public statement must include at least:

- observation period;
- exact corpus SHA-256;
- exact benchmark SHA-256;
- terminal operation count;
- truth population and truth coverage;
- OTR, false-opportunity rate and route-survival rate;
- frozen fee/slippage/threshold assumptions;
- exact venue and route scope;
- paper-only and top-of-book limitations.

No headline percentage should be published while the report is `NOT_READY`.

## Safety boundary

The campaign:

- uses public read-only market data;
- stores no exchange credentials;
- places no orders;
- signs no transactions;
- controls no wallet;
- transfers no funds;
- allocates no live capital;
- automatically promotes no policy.
