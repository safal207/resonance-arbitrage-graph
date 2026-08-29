# Corpus Campaign 002 — measurement-corrected real-market evidence

## Purpose

Campaign 002 is a fresh, dedicated public-market corpus created after Campaign
001 exposed two measurement problems:

1. Kraken price-level `publication_ts` had been treated as the freshness clock
   of the complete client-observed snapshot;
2. five requested HTTP samples were collected inside a five-second window, so
   acquisition overhead could trim the first sample and leave an incomplete
   rolling window.

Campaign 001 is retained unchanged as a fail-closed diagnostic artifact.
Campaign 002 does not import, relabel or reinterpret any Campaign 001 record.

## Bound measurement policy

```text
venue                  Kraken Spot public PreTrade
starting state         KRAKEN_SPOT:USD
paper capital          1,000 USD per logical operation
fee assumption         10 bps per leg
slippage assumption     2 bps per leg
execution threshold     5 bps net edge
outcome horizon         60 seconds
rolling samples         5
rolling interval        1 second
rolling horizon         10 seconds
minimum coverage        0.5
snapshot freshness      client observation time
level timestamp         preserved source provenance
```

These values are explicit research assumptions, not claims about a particular
account tier and not trading recommendations.

The ten-second rolling horizon deliberately exceeds the nominal four-second
inter-sample span. Public HTTP acquisition time is part of the real collection
process; it must not silently delete one of the five required samples.

## Candidate definition

Campaign 002 treats a candidate as a multi-market cycle. An immediate two-leg
buy/sell reversal on one top-of-book pair is excluded:

```text
USD -> BTC -> USD on the same market
```

That path measures spread and modeled costs; it does not express an arbitrage
hypothesis. Keeping it in the candidate population would consume limited scan
slots and inflate rejection counts without testing cross-market consistency.
The current CEX graph therefore admits the three-leg triangular cycles while
retaining ordinary two-leg round trips for separate negative-control testing.

## Profiles

Campaign 002 uses five equal-capital Kraken USD triangular market sets:

- BTC / ETH / USD;
- BTC / SOL / USD;
- BTC / ADA / USD;
- BTC / XRP / USD;
- BTC / LTC / USD.

The artificial 250,000 USD capacity-stress profile from Campaign 001 is excluded
from this product-proof corpus. Capacity stress remains useful adversarial QA,
but mixing a deliberately oversized profile into a headline opportunity metric
would distort the product claim.

## Evidence path

```text
current public snapshot
→ complete rolling evidence
→ candidate cycles
→ deterministic verifier
→ regime gate
→ decision persisted before waiting
→ 60-second public outcome snapshot
→ independently recomputed paper edge
→ append-only corpus record
→ Opportunity Truth Benchmark v0.2
```

All evidence is written only beneath `campaign/002` on the dedicated
`data/corpus-campaign-002` branch. The report must fully reproduce from the
bound corpus before it is committed.

## Readiness

Automated readiness requires all of the following:

- at least 100 terminal logical operations;
- at least 30 determinate truth events;
- at least 20 decision batches;
- at least 10 effective decision batches;
- at least one hour of temporal span;
- at least three route topologies;
- at least two effective routes;
- at least three route markets;
- at least two derived market regimes.

Passing these gates means only `INTERNAL_EVIDENCE_READY`. It is not publication
approval, real-fill profitability, strategy promotion or permission to trade.

If realistic costs produce no `EXECUTE_SIM` truth population, that is a valid
product finding. The project must then report the opportunity funnel and the
reasons visible spreads were rejected rather than lowering costs or thresholds
after seeing the outcomes.

## Safety boundary

Public read-only market data and paper evaluation only. No credentials, private
account APIs, orders, signing, transfers, wallet control, live capital or
automatic policy activation.
