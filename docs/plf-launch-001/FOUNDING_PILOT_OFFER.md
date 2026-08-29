# RESONANCE Verify — Founding Design-Partner Pilot

## Purpose

Help one trading-agent team discover where apparently valid proposed trades fail before or shortly after the execution boundary — without replacing its strategy, custody, accounts, or executor.

## Pilot scope

- 14 calendar days;
- one strategy or decision workflow;
- one venue;
- one agreed route/market family;
- public, fixture, or sandbox data only;
- async email and shared evidence;
- paper verification only.

## Deliverables

1. **Opportunity funnel**
   - captured proposals;
   - evidence completeness;
   - structural-pass rate;
   - gross-positive population;
   - net-positive population after agreed costs;
   - policy-eligible population.

2. **False-opportunity map**
   - freshness;
   - depth/capacity;
   - slippage/cost drag;
   - latency or edge decay;
   - market regime;
   - policy/permission boundary;
   - missing or ambiguous evidence.

3. **Evidence examples**
   - reproducible ALLOW / OBSERVE / REJECT cases;
   - reason codes;
   - source and decision digests;
   - replay instructions.

4. **Integration recommendation**
   - where verification should sit;
   - CLI / SDK / API / MCP / replay-report recommendation;
   - latency and payload requirements;
   - what remains owned by the existing stack.

## What the design partner keeps

- strategy and signal IP;
- exchange accounts;
- custody and keys;
- execution infrastructure;
- live risk decisions;
- ownership of production deployment.

## Explicit exclusions

The pilot does not:

- place or route orders;
- request exchange credentials or wallet keys;
- sign transactions;
- transfer or custody assets;
- promise profitability;
- certify a strategy for production;
- represent paper top-of-book outcomes as live fills.

## Price hypothesis

Working discovery range: **USD 750–1,500**.

Final price depends on:

- data preparation effort;
- number of evidence sources;
- custom route/policy mapping;
- requested integration prototype;
- reporting depth.

The range is a hypothesis, not a published fixed tariff. It should be tested after the prospect confirms a costly, recurring problem.

## Pilot acceptance gate

Proceed only when the partner provides in writing:

- the bounded paper-only scope;
- the strategy/workflow being evaluated;
- the public/fixture/sandbox evidence source;
- the decision owner;
- the success question;
- agreement that no live performance guarantee is made.

## Pilot success

The pilot succeeds when it produces an actionable decision, even if that decision is not to buy software:

- adopt a pre-trade verifier;
- improve existing controls;
- add replay/audit infrastructure;
- change cost/depth assumptions;
- conclude that the current problem is not commercially urgent.
