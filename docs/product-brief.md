# RESONANCE Verify — Product Brief

## Product thesis

Trading agents can propose actions faster than teams can verify whether those actions are still executable. RESONANCE Verify is the independent, evidence-producing layer between a market signal and an execution system.

```text
proposal
→ deterministic pre-trade verification
→ paper verdict
→ reproducible evidence
→ later outcome
→ truth benchmark
```

The wedge is not “another arbitrage scanner.” The wedge is **pre-trade decision verification for autonomous financial agents**.

## Job to be done

> When my system proposes a market action, help me decide whether the opportunity is still real under explicit constraints, and give me evidence I can replay later.

The customer is not buying a raw spread. They are buying fewer false opportunities, a reviewable decision boundary, and an audit trail connecting prediction to outcome.

## First ideal customer profile

### Primary: agentic trading builders

Teams with an existing signal or action-proposal layer and an execution/risk layer, but no independent causal verifier between them.

Typical architecture:

```text
agent / strategy
→ proposed route
→ ad-hoc checks
→ execution
```

RESONANCE insertion point:

```text
agent / strategy
→ RESONANCE Verify
→ EXECUTE_SIM / OBSERVE / REJECT
→ existing risk or execution stack
```

### Secondary: quant and trading infrastructure teams

Teams that want an independent replay and strategy-QA harness without sharing or replacing their alpha-generation logic.

### Later: wallet intelligence

The later adjacent product is verified follower edge: not “what did a wallet do?”, but “is the action still reproducible by a follower after delay and costs?”. This remains outside Product 0.1.

## Product promise

**Input:** a proposed route, exact market observations, capital, costs and policy.

**Output:**

- deterministic paper verdict;
- explicit reason codes;
- expected edge after modeled constraints;
- exact evidence SHA and replay material;
- later truth classification and benchmark contribution.

## Differentiation

Most products emphasize one of two layers:

```text
signal generation
or
execution
```

RESONANCE Verify owns the boundary between them:

```text
signal
→ is this still executable?
→ evidence
→ execution decision
```

The moat is the full learning loop:

```text
proposal
→ verification
→ evidence
→ outcome
→ truth metric
→ replay
→ calibration
→ governed policy
```

## Product maturity

### Implemented

- public Binance/Kraken quote normalization;
- graph route verification;
- fee/slippage/capacity/freshness/latency modeling;
- rolling market regime evidence;
- monotonic execution gate;
- append-only outcome memory and real-market corpus;
- replay, holdout and walk-forward evaluation;
- leakage-safe predictive shadow evaluation;
- policy promotion, lineage, revocation and authority;
- corpus quantity and diversity readiness gates;
- Opportunity Truth Benchmark report.

### Not yet proven

- a claim-ready real-market benchmark corpus;
- external users or paid design partners;
- a hosted API SLA;
- improvement over a partner’s existing verifier;
- live-fill or live-PnL performance.

## North-star evidence

The primary product proof is not repository version count. It is a reproducible benchmark over real captured market evidence.

Core measures:

- determinate `EXECUTE_SIM` truth events;
- Opportunity Truth Rate by route and regime;
- False Opportunity Rate;
- Route Survival Rate;
- expected-to-observed edge decay;
- paper PnL by exact starting state;
- concentration and diversity of the evidence corpus.

## Product gates

### Gate 1 — internal evidence readiness

The real-market corpus must pass explicit quantity, time-span, route, market and regime diversity thresholds plus a minimum truth-event count.

### Gate 2 — design-partner relevance

At least three target teams confirm that the pre-execution verification gap is real and provide one concrete integration or evaluation scenario.

### Gate 3 — comparative value

On untouched partner or public evidence, RESONANCE must demonstrate one or more of:

- fewer false-positive actions;
- better calibrated opportunity survival;
- clearer reason codes;
- stronger replay/audit evidence;
- lower operational effort to investigate a decision.

Only after these gates should the team choose between hosted API, SDK, wallet expansion or additional model research.

## Design-partner question

The opening question is deliberately non-salesy:

> When your trading agent sees an opportunity, how do you verify it is still executable before letting it act?

Follow-up discovery areas:

1. What proposes the action today?
2. What hard checks happen before execution?
3. Which false positives are most expensive?
4. How are fees, depth, quote age and latency modeled?
5. Can the team replay the exact original decision later?
6. What evidence would they trust from an external verifier?
7. Would integration happen as library, API, sidecar or offline benchmark?
8. What would make a two-week paper pilot valuable?

## Initial pilot hypothesis

A narrow design-partner pilot should remain paper-only:

1. ingest a partner-supplied or public candidate stream;
2. mirror decisions without affecting execution;
3. return `EXECUTE_SIM / OBSERVE / REJECT` plus evidence;
4. resolve later paper outcomes;
5. deliver an Opportunity Truth Benchmark and top false-opportunity causes.

The pilot sells **measurement and verification**, not promised trading returns.

## Business-model hypothesis

Do not lock pricing before discovery. Plausible later models:

- fixed-fee verification pilot;
- metered verification API;
- monthly replay/benchmark subscription;
- enterprise self-hosted verifier with support;
- independent strategy QA engagement.

The first commercial offer should be a bounded paid pilot with a clear corpus, horizon, report and decision-review deliverable.

## Explicit non-goals for Product 0.1

- no live trading;
- no custody or wallet control;
- no automatic capital allocation;
- no cross-venue execution claim without inventory/rebalance modeling;
- no new deep/RL model before real evidence is adequate;
- no universal “best route” or guaranteed-profit claim;
- no broad wallet intelligence build before wedge validation.
