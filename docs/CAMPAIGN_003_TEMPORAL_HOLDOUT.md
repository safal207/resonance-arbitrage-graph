# Campaign 003 — pre-registered temporal holdout (gross-positive cycles only)

## Research question

Campaign 002 observed gross-positive, structurally eligible Kraken USD triangular routes in:
- **16:00–16:59 UTC:** 7/30 (23.33%) of sampled terminal routes;
- **01:00–01:59 UTC:** 19/158 (12.03%).

The 16:00 hour was selected **after** looking at Campaign 002. Those numbers
generate the hypothesis but **must never be used as confirmatory evidence**.
No other historical hour will be substituted after looking at the holdout.

This is **not a claim of positive net edge**, realized profit, executable
trades, or a causal time-of-day effect. Campaign 002 showed **zero** net-positive
routes under the fixed cost assumptions.

## Freeze before collecting any Campaign 003 data

- Source: a NEW dedicated, append-only `data/corpus-campaign-003` branch;
  no records imported from Campaign 001/002; a new policy manifest and record
  identity are required.
- Venue: **Kraken Spot public, read-only, paper-only**.
- Market universe: BTC/USD plus ETH/BTC, SOL/BTC, ADA/BTC, XRP/BTC, LTC/BTC
  and each corresponding asset/USD pair.
- Capital: USD 25 per logical operation.
- Route population: two directions of three-leg triangular cycles per asset:
  `USD -> BTC -> asset -> USD` and `USD -> asset -> BTC -> USD`.
- Costs: exactly **10 bps fee + 2 bps slippage + 0 bps gas PER LEG**.
- Pre-trade `EXECUTE_SIM` threshold: **5 bps net**; quote age ≤3000 ms.
  Never lower costs or thresholds on the same evidence to generate positives.
- Outcome: a **gross-positive** route means the existing Opportunity Funnel
  classifier `_build_row(case).gross_positive`, which requires complete
  market regime evidence, passing structural constraints, and gross edge >0.
  Do not count rejected-by-capacity or unknown-regime cases as positive.
- Holding period/outcome acquisition: retain 60-second paper-only future
  outcome resolution, with no outcome visible at decision time.
- Primary comparison (frozen): **UTC hour 16** versus **UTC hour 01**,
  paired by UTC calendar day. Do not choose new hours after analyzing data.
- Time interval: **2026-12-01 through 2026-12-28 UTC inclusive**,
  28 calendar days, determined BEFORE any new samples. Each day/slot
  should capture exactly 10 terminal routes (five assets × two directions).
  This makes the planned maximum 560 candidate routes (28 × 2 × 10).
- Target sampling: once per slot per day. GitHub Actions delays can shift
  actual decision time; classification uses the timestamp from the **actual
  evidence** in UTC, not the scheduled cron hour. Out-of-slot, duplicate,
  changed-cost and changed-market records fail closed.
- No one-off resampling of just losing slots, post-hoc exclusions, or
  retroactive date / hour / capital / fee changes.

**Operational note:** This PR adds the preregistration and a read-only evaluator.
It does NOT automatically schedule or launch data acquisition, and it does
NOT create `data/corpus-campaign-003`. Collection automation is a **separate,
reviewable and bounded** decision after the protocol has been frozen.
If collection does not occur within the interval, the result is inconclusive,
not a time effect.

## Predefined analysis

1. Verify the independent corpus' canonical hash chain with `load_corpus`.
   Reject any use of Campaign 002's corpus SHA.
2. Reconstruct every route using the original replay engine and Opportunity
   Funnel definition. Verify exact venue, route shape, markets, costs, amount,
   and execution-threshold policy.
3. Bucket each terminal operation by actual `evaluation_time_ms` in UTC,
   without shifting timestamps to a chosen hour. Exactly one operation per
   asset/direction/day/slot; reject duplicates and out-of-plan observations.
4. A **complete paired day** has ten valid terminal routes in BOTH UTC slots.
   Report all 28 days and list incomplete pairs. Never silently inflate
   denominators or fill in missing cases. Minimum usable coverage:
   **24 complete paired days of 28**. If fewer: `INCONCLUSIVE_COVERAGE`.
5. On complete days, calculate each slot's gross-positive rate per *all*
   scheduled terminal candidates (not per positive or structurally eligible
   candidates). Primary effect: `rate_16 - rate_01`.
6. For each paired day, compare its integer gross-positive counts between
   slots, with wins/losses/ties. Use a two-sided **exact sign test** on
   non-tied paired days. This treats the day (rather than correlated
   individual routes) as the testing unit.
7. Label `REPLICATED_GROSS_PATTERN` **only if all three hold**:
   - ≥24 complete day pairs;
   - positive rate difference ≥**10 percentage points**;
   - UTC16 wins more paired days than it loses, with exact two-sided
     sign-test **p ≤ 0.05**.
   Otherwise, if coverage passes, `NOT_REPLICATED`. Neither outcome
   constitutes causal evidence or demonstrates a tradable advantage.
8. Report number of complete/missing days, all 28 daily counts, times,
   paired-day test, both rates, net-positive total, and source corpus SHA.
   Do not label undefined OTR as 0%.

**Statistical limits:** Days may be serially correlated; the paired-day sign
test is an evidence screen, not a causal randomized experiment. If market
conditions or sampling schedule systematically differ across arms,
interpretation remains limited. Even a positive gross pattern could be
negative after modeled costs. Secondary asset/regime analyses are descriptive,
and any new hypothesis requires another **new**, pre-registered holdout.

## How to evaluate

Once an independent, fully validated Campaign 003 corpus actually exists:

```bash
python -m resonance_arbitrage_graph.temporal_holdout \
  campaign/003/corpus.json \
  --output campaign/003/temporal-holdout-v0.1.json
```

The evaluator cannot fabricate missing future evidence. It is intentionally
unconnected to exchange credentials, order placement, or automatic strategy
promotion.

Source of historical hypothesis: [Campaign 002 evidence audit
PR #87](https://github.com/safal207/resonance-arbitrage-graph/pull/87)
and [campaign issue #57](https://github.com/safal207/resonance-arbitrage-graph/issues/57).
