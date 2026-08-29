# Corpus Campaign 002 — measurement-corrected real-market evidence

## Purpose

Campaign 002 is a fresh, dedicated public-market corpus created after Campaign
001 exposed three measurement problems:

1. Kraken price-level `publication_ts` had been treated as the freshness clock
   of the complete client-observed snapshot;
2. five requested HTTP samples inside a five-second window were vulnerable to
   acquisition jitter trimming the first sample and forcing `UNKNOWN`;
3. immediate two-leg buy/sell round trips consumed candidate slots despite
   being spread/cost negative controls rather than arbitrage hypotheses.

Campaign 001 is retained unchanged as a fail-closed diagnostic artifact.
Campaign 002 does not import, relabel or reinterpret any Campaign 001 record.

## Bound measurement policy

```text
venue                  Kraken Spot public PreTrade
starting state         KRAKEN_SPOT:USD
paper capital          25 USD per logical operation
fee assumption         10 bps per leg
slippage assumption     2 bps per leg
execution threshold     5 bps net edge
outcome horizon         60 seconds
route population        three-leg triangular cycles only
rolling samples         6
rolling interval        1 second
rolling horizon         10 seconds
minimum coverage        0.5
snapshot freshness      client observation time
level timestamp         preserved source provenance
```

These values are explicit research assumptions, not claims about a particular
account tier and not trading recommendations.

Six samples create five intended inter-sample intervals. The ten-second horizon
keeps all six samples despite ordinary public-HTTP acquisition jitter, while the
50% coverage gate still requires at least five seconds of observed market time.

## Why USD 25

Campaign 001 used USD 1,000 and repeatedly exceeded top-of-book capacity on
thin cross pairs. That measured the chosen notional more often than route edge.
Campaign 002 uses a micro-notional so the normal corpus can test triangular
route economics and 60-second survival without bypassing capacity: every route
is still checked against exact top-of-book quantity.

A deliberately oversized capacity profile remains useful adversarial QA, but it
stays outside the headline Opportunity Truth corpus so it cannot distort the
product metric.

## Candidate definition

Campaign 002 treats a candidate as a multi-market cycle. An immediate two-leg
buy/sell reversal on one top-of-book pair is excluded:

```text
USD -> BTC -> USD on the same market
```

That path measures spread and modeled costs; it does not express an arbitrage
hypothesis. Keeping it in the candidate population would consume limited scan
slots and inflate rejection counts without testing cross-market consistency.
The current CEX graph therefore admits the two three-leg triangular directions
for each profile while retaining ordinary two-leg round trips as unit-test
negative controls.

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
→ triangular candidate cycles
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
