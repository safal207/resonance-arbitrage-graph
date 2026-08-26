# Product 0.1.1 — Opportunity Truth Benchmark v0.2

This document defines how RESONANCE Verify turns captured paper-market evidence into an **internal product-evidence status** without mixing fixtures, future information, correlated market moments or incompatible PnL units into a headline metric.

The benchmark is not a profitability guarantee and automated readiness is not permission to publish a claim.

## Product hypothesis

A visible arbitrage signal often overstates executable opportunity quality.

RESONANCE Verify creates measurable value if its `EXECUTE_SIM` population has stronger later paper outcomes than the raw candidate population and if the system can explain why downgraded or rejected candidates failed.

## Unit of analysis

The unit is one collapsed `logical_operation_id`, not one retry row.

```text
candidate detection
→ one decision identity
→ zero or more retries
→ one latest outcome state
→ one benchmark row
```

Retries cannot inflate TP/FP counts.

## Evidence source classes

### Real-market corpus

A `RealMarketReplayCorpus` contains append-only public-market decision and outcome records. It is the only source class eligible for automated internal evidence readiness.

### Replay bundle

A `ReplayBundle` remains valid for software tests, fixtures and deterministic diagnostics. Its claim status is always:

```text
UNASSESSED_REPLAY_SOURCE
```

A large synthetic replay population does not become a real-market claim merely because it passes a sample-size threshold.

## Decision funnel

```text
candidate
├─ EXECUTE_SIM
│  ├─ TRUE_POSITIVE
│  ├─ FALSE_POSITIVE
│  ├─ EXPIRED
│  └─ INDETERMINATE
├─ OBSERVE
└─ REJECT
```

`REJECT` is not a false positive because the verifier never claimed that route was executable. `OBSERVE` and unresolved outcomes do not enter the Opportunity Truth Rate denominator.

## Primary metrics

### Opportunity Truth Rate

```text
OTR = TRUE_POSITIVE / (TRUE_POSITIVE + FALSE_POSITIVE)
```

### False Opportunity Rate

```text
FOR = FALSE_POSITIVE / (TRUE_POSITIVE + FALSE_POSITIVE)
```

### Route Survival Rate

```text
Route Survival = (TP + FP) / (TP + FP + EXPIRED)
```

Expiration remains a separate failure mode.

### Truth coverage

```text
Truth Coverage = (TP + FP) / EXECUTE_SIM
```

A high OTR with low truth coverage is not strong product evidence. The report exposes both.

### Edge decay

```text
Edge Decay = mean(expected_edge_bps) - mean(observed_edge_bps)
```

Edge means are calculated only for determinate TP/FP outcomes.

## Unit-safe paper PnL

For one determinate `EXECUTE_SIM` operation:

```text
expected_pnl_units = start_amount × expected_edge_bps / 10,000
observed_pnl_units = start_amount × observed_edge_bps / 10,000
```

The units belong to the exact starting state:

```text
venue:asset
```

Therefore the v0.2 report groups PnL separately, for example:

```text
binance:USDT
kraken:EUR
fixture:BTC
```

It never adds BTC, ETH, USDT, EUR or balances on different venues into one fake global total. The v0.1 aggregate PnL remains embedded only as legacy evidence and is explicitly not used as the v0.2 product metric.

## Claim policy

Default internal-readiness guardrails:

```text
min_terminal_operations = 100
min_truth_events = 30
require_corpus_quality = true
```

`terminal_operations` and `truth_events` are different gates. A corpus can contain many terminal rejections or expirations without enough determinate TP/FP outcomes.

## Corpus quality gate

Sample size alone is insufficient. Thirty nearly identical observations captured in one market moment do not provide the same evidence as diverse chronological observations.

The v0.2 report binds the existing `CorpusQualityPolicy` and `CorpusQualityReport`, including:

- distinct decision batches;
- effective decision-batch count;
- temporal span;
- distinct route topologies;
- effective route count;
- distinct route markets;
- distinct derived regimes;
- concentration diagnostics;
- failed quality dimensions;
- exact corpus SHA-256.

A corpus can pass terminal and truth counts while still receiving `NOT_READY` because evidence is too concentrated.

## Statuses

```text
NOT_READY
```

A real-market corpus exists, but one or more quantity, truth-population or quality guardrails fail.

```text
INTERNAL_EVIDENCE_READY
```

The automated real-market quantity and quality checks pass. This means the evidence is ready for internal product review. It does **not** mean:

- publication is approved;
- profitability is proven;
- statistical significance is established;
- live fills were observed;
- future performance is guaranteed;
- a policy may be activated.

```text
UNASSESSED_REPLAY_SOURCE
```

The report was produced from a replay bundle without real-market corpus provenance.

## Canonical evidence

The v0.2 envelope binds:

- evidence source class;
- source SHA-256;
- replay-bundle SHA-256;
- exact sorted logical-operation membership;
- the complete verified v0.1 benchmark payload and SHA;
- claim policy and SHA;
- corpus-quality payload and SHA when applicable;
- terminal and truth populations;
- truth coverage;
- expected/observed edge and edge decay;
- unit-safe paper PnL slices;
- explicit paper-only and non-publication flags.

Structural verification checks canonical form, semantic invariants and hashes. Full verification rebuilds the complete v0.2 report from the supplied corpus or replay bundle.

## CLI

Build JSON and Markdown:

```bash
resonance-opportunity-truth-benchmark build real-market-corpus.json \
  --output opportunity-truth-v0.2.json \
  --markdown-output opportunity-truth-v0.2.md
```

Useful explicit guardrails:

```bash
resonance-opportunity-truth-benchmark build real-market-corpus.json \
  --min-terminal-operations 100 \
  --min-truth-population 30 \
  --min-decision-batches 20 \
  --min-effective-decision-batches 10 \
  --min-temporal-span-ms 3600000 \
  --min-distinct-routes 3 \
  --min-effective-routes 2 \
  --min-distinct-route-markets 3 \
  --min-distinct-regimes 2 \
  --output benchmark.json
```

Full source-bound verification:

```bash
resonance-opportunity-truth-benchmark verify \
  real-market-corpus.json \
  benchmark.json
```

Render an already verified envelope:

```bash
resonance-opportunity-truth-benchmark render \
  benchmark.json \
  --output benchmark.md
```

## Publication rule

Do not copy a favorable number into marketing material without preserving and reviewing:

- report SHA;
- source corpus SHA;
- claim status and blockers;
- terminal and truth populations;
- truth coverage;
- corpus-quality evidence;
- route/regime segmentation from the bound legacy benchmark;
- unit identity for every PnL number;
- paper-only interpretation.

## Design-partner question

Start with the operational gap rather than the architecture:

> **When your trading agent sees an opportunity, how do you verify it is still executable before letting it act?**

Product 0.1.1 is successful when real evidence can answer that question with a reproducible verdict, an honest readiness status and metrics that cannot silently mix incompatible units.
