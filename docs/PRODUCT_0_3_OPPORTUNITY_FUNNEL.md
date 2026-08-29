# Product 0.3 — Opportunity Funnel Benchmark

## Why this report exists

Opportunity Truth Rate grades only opportunities that reached `EXECUTE_SIM` and
later produced a truth outcome. That denominator can legitimately be empty.

The first measurement-corrected Campaign 002 run produced complete `NORMAL`
market evidence and capacity-valid triangular routes, but none had a positive
raw cross-rate before modeled costs. Calling OTR `0%` would be mathematically
and product-wise wrong: no signal was authorized for simulation, so there was
nothing to grade as a true or false positive.

The Opportunity Funnel answers the earlier question:

> At which causal layer did each captured market cycle stop being an executable
> opportunity?

## Cumulative stages

```text
captured terminal cycle
→ complete market/regime evidence
→ structural constraints pass
→ gross-positive before costs
→ net-positive after modeled costs
→ execute-threshold eligible
→ final EXECUTE_SIM after regime gate
→ resolved execute outcome
→ TP + FP truth outcome
→ required edge survived
```

Each stage is a subset of the previous stage. Empty downstream stages are valid
evidence and do not cause the report to invent a percentage.

## Blocker classes

The report preserves both an exclusive first blocker and grouped blocker
counts.

Structural blockers include:

- incomplete/`UNKNOWN` evidence;
- stale quote;
- insufficient capacity;
- route latency;
- low execution/settlement confidence;
- invalid cycle shape.

Economic or downstream blockers include:

- gross cross-rate is non-positive;
- modeled fees/slippage erase a gross-positive edge;
- positive net edge remains below the bound execute threshold;
- evidence-derived regime gate downgrades the route;
- execute opportunity expires or lacks a realized outcome;
- realized paper edge does not clear the required threshold.

A route rejected before `EXECUTE_SIM` is **not** a false positive. False
positive retains its narrower meaning: the verifier authorized `EXECUTE_SIM`,
but the later paper outcome failed the bound required edge.

## Edge distributions

For every terminal candidate, the report binds:

- gross edge before costs;
- expected net edge after the exact per-leg cost assumptions;
- modeled cost drag (`gross - net`);
- later observed edge when an outcome quote was captured.

Observed edge is reported even for rejected candidates as a diagnostic of market
movement, but it does not retroactively change the decision-time verdict.

## Evidence contract

`OpportunityFunnelReport` is deterministic canonical JSON with SHA-256. It
binds:

- exact real-market corpus or replay-bundle SHA;
- exact replay-bundle SHA;
- sorted logical-operation membership;
- overall cumulative counts and distributions;
- route and regime slices;
- first, structural and economic blocker distributions;
- explicit diagnostic/paper-only interpretation flags.

Verification rebuilds the complete report from the supplied source. Recomputing
only the outer digest is insufficient.

## CLI

```bash
resonance-opportunity-funnel build campaign/002/corpus.json \
  --output campaign/002/opportunity-funnel-v0.1.json \
  --markdown-output campaign/002/opportunity-funnel-v0.1.md

resonance-opportunity-funnel verify \
  campaign/002/corpus.json \
  campaign/002/opportunity-funnel-v0.1.json
```

Campaign 002 rebuilds and fully verifies both the funnel and the Opportunity
Truth Benchmark before committing either report to the append-only data branch.

## Product interpretation

The two reports answer different questions:

```text
Opportunity Funnel
  = where did observed cycles disappear?

Opportunity Truth Rate
  = among authorized EXECUTE_SIM signals, how many survived?
```

A strong pre-trade verifier may initially create value by proving that most
visible cycles never become executable opportunities. The product must report
that filtration honestly rather than lower fees, slippage or thresholds after
seeing the same outcomes.

## Safety boundary

Public/read-only evidence and paper analysis only. No credentials, private
account endpoints, orders, signing, transfers, wallets, live capital or
automatic policy changes.
