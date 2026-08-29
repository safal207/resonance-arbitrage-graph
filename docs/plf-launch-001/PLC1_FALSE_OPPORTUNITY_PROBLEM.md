# The False Opportunity Problem

## A visible spread is not yet an executable trade

Trading systems are very good at noticing price differences. The dangerous leap is treating every visible difference as an opportunity that survived the path to execution.

A proposed trade still has to survive:

```text
route continuity
→ available depth
→ quote freshness
→ market regime
→ fees
→ slippage
→ required edge
→ later outcome
```

RESONANCE Verify records each boundary separately instead of collapsing everything into one optimistic signal.

## What the first measurement-corrected sample showed

Campaign 002 captured 20 terminal triangular cycles from public Kraken top-of-book data under a fixed paper policy:

- public/read-only market data;
- USD 25 paper notional for normal profiles;
- 10 bps modeled fee per leg;
- 2 bps modeled slippage per leg;
- three-leg triangular cycles;
- 5 bps required post-cost edge;
- 60-second outcome horizon;
- no orders, credentials, signing, transfers, custody, or live capital.

The cumulative funnel was:

```text
Captured terminal cycles             20
Complete evidence                    20
Structural constraints pass          19
Gross-positive before costs           2
Net-positive after modeled costs      0
Execute-threshold eligible            0
Final EXECUTE_SIM                      0
```

Mean modeled cost drag was **35.94 bps**. The best gross edge observed in this sample was **1.65 bps**.

So two cycles looked positive before costs, and neither remained positive after the fixed cost model.

## What this does — and does not — prove

It supports one bounded statement:

> In this 20-cycle public-data sample, gross-positive price relationships did not survive the fixed modeled costs.

It does **not** prove:

- that crypto arbitrage never exists;
- that the Opportunity Truth Rate is 0%;
- that the modeled costs match every account tier or live fill;
- that future market conditions will look the same;
- that RESONANCE generated profit or prevented a realized loss.

OTR is unavailable here because no candidate entered `EXECUTE_SIM`; therefore there is no TP/FP denominator to grade.

## Why this matters for autonomous agents

A human trader may notice that a spread is tiny relative to costs. An autonomous agent can repeat the same mistake at machine speed unless the execution boundary is explicit.

The useful question is not only:

> Did the agent find a signal?

It is:

> Which evidence survived before the signal was allowed to become an action?

That is the gap RESONANCE Verify is designed to fill.

## Reproducibility

- corpus branch: `data/corpus-campaign-002`
- source corpus SHA-256: `30db7b133da15417b49bc21c43593e1aaf5ac1482ae192b87bc85fde1797b733`
- funnel evidence SHA-256: `4cfc07bb0451a7566cc4aee1fdbc59fd20d766731a885ff356dfe70d1cc1727b`

## The question for trading-agent builders

When your agent finds a trade that looks profitable, what evidence must survive before it may submit the order — and which failure is hardest to catch today: stale price, slippage, thin liquidity, policy breach, or an unexplained decision?

To share one public, fixture, or sandbox example, email `safal0645@gmail.com` with the subject **Opportunity Truth example**. No credentials or sensitive production architecture are needed.
