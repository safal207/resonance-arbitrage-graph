# Opportunity Truth Benchmark

## Purpose

The Opportunity Truth Benchmark is the product-proof layer for RESONANCE Verify. It answers:

> Of the opportunities evaluated by the deterministic paper verifier, which ones later remained valid under the bound outcome evidence?

It does not optimize a model, select a trading policy, or place an order.

## Sources

The benchmark accepts:

1. `RealMarketReplayCorpus` — append-only public-market decision and outcome evidence;
2. `ReplayBundle` — deterministic replay fixtures or exported corpus data.

A `ReplayBundle` can produce useful diagnostics, but it receives `UNASSESSED_REPLAY_SOURCE`. Product claim readiness requires real-market corpus provenance and its bound corpus-quality report.

## Decision funnel

Each collapsed logical operation contributes exactly one current row.

```text
candidate
├─ EXECUTE_SIM
│  ├─ TRUE_POSITIVE
│  ├─ FALSE_POSITIVE
│  ├─ EXPIRED
│  └─ INDETERMINATE / pending
├─ OBSERVE → INDETERMINATE
└─ REJECT  → REJECTED
```

Retries never increase the number of candidate opportunities.

## Metrics

### Opportunity Truth Rate

```text
OTR = TRUE_POSITIVE / (TRUE_POSITIVE + FALSE_POSITIVE)
```

Only determinate opportunities that the system classified `EXECUTE_SIM` enter the denominator.

### False Opportunity Rate

```text
FOR = FALSE_POSITIVE / (TRUE_POSITIVE + FALSE_POSITIVE)
```

A deterministic `REJECT` is not a false positive. The verifier never claimed that opportunity was executable.

### Route Survival Rate

```text
Route Survival Rate =
  (TRUE_POSITIVE + FALSE_POSITIVE)
  / (TRUE_POSITIVE + FALSE_POSITIVE + EXPIRED)
```

This measures whether `EXECUTE_SIM` candidates remained observable long enough to receive a determinate later paper edge.

### Truth Coverage

```text
Truth Coverage =
  (TRUE_POSITIVE + FALSE_POSITIVE) / EXECUTE_SIM
```

Low truth coverage warns that OTR is based on too small a resolved subset.

### Edge decay

```text
Edge Decay = expected_edge_bps - observed_edge_bps
Prediction Error = observed_edge_bps - expected_edge_bps
```

The report includes means only over determinate truth events.

## Paper PnL units

For one operation:

```text
expected paper PnL units = start_amount × expected_edge_bps / 10,000
observed paper PnL units = start_amount × observed_edge_bps / 10,000
```

These units are meaningful only in the operation’s exact starting asset and venue state. The benchmark groups them by:

```text
venue:asset
```

It never sums USDT, BTC, ETH or balances held on different venues into one fake currency total.

Public future top-of-book edge is still not a real fill, realized account PnL or proof of executable settlement.

## Segmentation

The report includes:

- overall funnel and metrics;
- exact market regime slices;
- semantic route slices;
- reason-code distribution;
- paper PnL by exact start state.

A global OTR must not hide a weak route or regime. Product interpretation should prefer segments with enough truth events.

## Claim readiness

`BenchmarkClaimPolicy` controls the minimum evidence needed for an internal product claim.

Default gates:

- at least 100 terminal real-market operations;
- at least 30 determinate truth events;
- corpus quality gate passes.

The existing corpus-quality gate checks:

- distinct and effective decision batches;
- temporal span;
- distinct and effective route topologies;
- distinct route markets;
- distinct market regimes.

Statuses:

```text
NOT_READY
  real-market evidence exists but quantity/truth/quality gates fail

INTERNAL_EVIDENCE_READY
  gates pass; suitable for internal product evidence review

UNASSESSED_REPLAY_SOURCE
  diagnostics came from ReplayBundle without real-market corpus claim provenance
```

`INTERNAL_EVIDENCE_READY` does not mean profitable, production-ready, statistically conclusive, or authorized for live trading.

## Canonical report

The report binds:

- source kind and source SHA;
- replay-bundle SHA;
- calibration-report SHA;
- exact logical-operation membership;
- claim policy and SHA;
- corpus quality report and SHA when present;
- all overall and segmented metrics;
- reason counts;
- paper PnL slices;
- safety semantics.

The envelope SHA protects canonical form. Full verification rebuilds the entire report from the supplied corpus or replay bundle.

## CLI

Build JSON:

```bash
resonance-opportunity-truth-benchmark build corpus.json \
  --output benchmark.json
```

Build Markdown directly:

```bash
resonance-opportunity-truth-benchmark build corpus.json \
  --format markdown \
  --output benchmark.md
```

Render an existing JSON report:

```bash
resonance-opportunity-truth-benchmark render benchmark.json \
  --output benchmark.md
```

Full source-bound verification:

```bash
resonance-opportunity-truth-benchmark verify benchmark.json corpus.json
```

## Publication rule

Do not manually copy a favorable percentage into marketing material without preserving:

- benchmark SHA;
- source corpus SHA;
- claim status;
- truth-event count;
- truth coverage;
- route/regime segment context;
- paper-only interpretation.

Until a real corpus is `INTERNAL_EVIDENCE_READY`, the public product page should say **benchmark pending**, not invent a number.
