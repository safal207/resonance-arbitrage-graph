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
2. verify the frozen campaign-policy manifest;
3. find matured pending cases for the exact venue and market set;
4. obtain a fresh public quote set;
5. recompute and append their outcomes;
6. verify the persisted corpus hash;
7. only then start the next one-shot capture.

Recovery never changes the original decision state. It appends a later attempt under the same `logical_operation_id`.

A pending case from another venue or market set is not touched. A quote observed before the configured horizon is rejected.

## Frozen recovery authority

The campaign writes `corpus.campaign-policy.json` **before the first decision capture**. The canonical manifest binds:

```text
campaign_id
venue
outcome horizon
paper-only / public-data boundary
```

Every later step must reproduce the exact policy SHA-256. A different campaign ID, venue or horizon fails closed. A pre-existing non-empty corpus without its original policy manifest cannot be silently adopted.

This prevents a later process from resolving a 60-second decision after only 10 seconds merely because the current CLI invocation supplied a shorter horizon.

The campaign-step receipt also proves:

```text
recovery.post_corpus_sha256
==
one_shot.pre_corpus_sha256
```

so the recovered state is the exact state consumed by the next capture.

## Campaign 001 frozen assumptions

The scheduled workflow uses Kraken public PreTrade data and several USD/BTC triangular market sets.

Paper-model assumptions are explicit and frozen in the workflow:

```text
campaign id:               corpus-campaign-001
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
campaign/001/corpus.campaign-policy.json
campaign/001/corpus.json
campaign/001/replay.json
campaign/001/opportunity-truth-v0.2.json
campaign/001/opportunity-truth-v0.2.md
campaign/001/receipts/<workflow-run>/<profile>.json
campaign/001/logs/<workflow-run>/<profile>.log
```

The corpus itself is append-only and hash-chained. Workflow commits bind the campaign files together as a transport/history layer; they do not replace the corpus and benchmark verification contracts.

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

## Scheduled operation and evidence budget

`.github/workflows/corpus-campaign-001.yml` runs twice per hour and can also be started manually.

Before trusting a stored stop state, the workflow fully reproduces the benchmark from the current corpus. A stale or altered report cannot stop collection.

Each profile failure is isolated and logged. Successful profiles still advance the corpus. The workflow fails only when no profile succeeds and no matured pending evidence is recovered.

After the profile steps, the workflow:

1. builds Opportunity Truth Benchmark v0.2 into temporary files;
2. performs full source-bound verification;
3. atomically publishes the verified JSON and Markdown;
4. commits updated evidence to the data branch;
5. uploads the same evidence as a workflow artifact.

Collection automatically stops when the verified report reaches `INTERNAL_EVIDENCE_READY`.

A hard evidence budget pauses the campaign after 2,000 terminal operations if readiness is still missing. That state requires product review rather than silently accumulating an unlimited corpus. Typical questions at that checkpoint are:

- are there too few `EXECUTE_SIM` events under the frozen cost assumptions;
- is one quality dimension structurally unreachable;
- should the claim or target market change;
- is another public venue needed;
- would further collection add evidence or merely repeat the same state.

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
