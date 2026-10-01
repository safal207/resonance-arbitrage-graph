# RESONANCE Verify: exchange-state drift before submission

This reproducible, offline demo compares an initial route permission with a fresh check immediately before **simulated submission**. It addresses the gap in which prices, available depth or exchange status can change after a candidate was validated.

All inputs are synthetic. No exchange, Quantilan system or private strategy was tested. This is a technical review fixture, with no order transmission or fill model.

## Run in a checkout

Python 3.11 or newer is sufficient. The demo and its focused tests use only the standard library; installation and network access are unnecessary.

```bash
# Check that the current code reproduces the committed report exactly.
PYTHONPATH=src python -m resonance_arbitrage_graph.exchange_state_demo \
  --fixture examples/quantilan/fixture.json \
  --check examples/quantilan/expected-report.json

# Produce a separate report for inspection.
PYTHONPATH=src python -m resonance_arbitrage_graph.exchange_state_demo \
  --fixture examples/quantilan/fixture.json \
  --output /tmp/quantilan-report.json

# Run the focused regression tests, including checks with network access disabled.
PYTHONPATH=src python -m unittest discover \
  -s tests -p test_exchange_state_demo.py -v
```

Expected replay output:

```text
Replay matches: 313084ae4464b057423496f800225015a4a2b565a0ae81be748aed02c0f5bad0
```

`--check` exits with 0 on an exact replay match, 1 on a mismatch, and 2 on invalid or unreadable input. Changed code bytes, policy, fixture values or results require an intentional report regeneration and review.

## Frozen assumptions

| Input | Fixture value |
|---|---|
| Venue | `SIMULATED` |
| Route | USDT → BTC → ETH → USDT; BUY BTCUSDT, BUY ETHBTC, SELL ETHUSDT |
| Starting amount | 1,000 synthetic USDT |
| Per-leg costs | 5 bps fee + 5 bps modeled slippage |
| `EXECUTE_SIM` threshold | Net edge ≥ 30 bps |
| `OBSERVE` band | 0 < net edge < 30 bps; no simulated submission |
| Quote age limit | 100 ms, inclusive |
| Initial check | Clock tick 1,000 ms, snapshot age 0 ms |
| Normal boundary check and simulated send | 1,080 ms, snapshot age 5 ms |
| Simulated arrival | 1,100 ms; a further 20 ms after the check/send |
| Stale-data case | Send at 1,180 ms, arrival at 1,200 ms, last observation at 1,000 ms |

These are illustrative parameters, not exchange measurements, recommended trading settings or the assumptions of Corpus Campaign 002. Clock values are synthetic monotonic ticks, not Unix timestamps. Engine route latency is zero in this fixture; the validation-to-submission and submission-to-arrival intervals are recorded separately.

The shared initial route has a modeled net edge of **+94.655365 bps**, so the first check returns `EXECUTE_SIM` in all seven cases.

## Results

The baseline copies the initial verdict and records an in-memory submission event. The guarded path rebuilds the route from the boundary snapshots, invokes the existing verifier, applies the fixture status gate, and records that event only when the final verdict is `EXECUTE_SIM`.

| Scenario | Reuse initial permission | Boundary recheck / submission | Retrospective arrival diagnostic |
|---|---|---|---|
| Unchanged, fresh observation | Submit | `EXECUTE_SIM` / yes | Eligible under the same model |
| BTC ask depth shrinks | Submit | `REJECT` / no | `CAPACITY_EXCEEDED:0` |
| ETH bid drops to 3,990 | Submit | `REJECT` / no | Net edge −54.895085 bps |
| ETH bid drops to 4,020 | Submit | `OBSERVE` / no | Net edge +19.880140 bps, below threshold |
| Exchange state becomes `HALTED` | Submit | `REJECT` / no | `EXCHANGE_NOT_TRADING:HALTED` |
| Snapshot becomes stale | Submit | `REJECT` / no | Snapshot remains too old |
| Depth shrinks after recheck | Submit | `EXECUTE_SIM` / yes | `CAPACITY_EXCEEDED:0`; residual race |

In `depth_shrink`, the BTC ask stays at 80,000 while available base quantity falls from 2 BTC to 0.0075 BTC. The first leg's capacity therefore falls from 160,000 to **600 USDT**, below the requested 1,000 USDT. Its modeled edge remains positive and its quote is only 5 ms old. Capacity alone changes the decision; this is not an example of the age limit catching the change.

The `exchange_halted` case adds an explicit **fixture-only status gate**. Existing `evaluate_route` does not ingest venue status. The report retains both the original engine receipt and the wrapper's status decision, so they are not confused with each other.

## What is reused and what is new

Existing `quote_to_trade_edges`, `evaluate_route` and `make_market_evidence_receipt` supply unit-aware capacity, costs, quote age, route continuity, verdicts and quote-to-edge provenance. The new demo module supplies explicit initial/boundary/arrival states, the synthetic status gate and the comparison trace. It does not change the core verifier or connect an execution adapter.

A stricter initial decision is never upgraded: `REJECT < OBSERVE < EXECUTE_SIM`. Both `OBSERVE` and `REJECT` prevent the in-memory submission event. The tests cover this rule, second-leg capacity units, the exact freshness threshold, future observations, stale input, invalid fixtures, replay mismatches and future-data isolation.

## Evidence and reproducibility

- [Frozen fixture](../examples/quantilan/fixture.json): all initial, boundary and arrival snapshots, route, costs, policy and times.
- [Expected report](../examples/quantilan/expected-report.json): both paths, reasons, timing gaps and full market evidence receipts.
- [Demo source](../src/resonance_arbitrage_graph/exchange_state_demo.py).
- [Regression tests](../tests/test_exchange_state_demo.py).

The report binds the canonical fixture SHA-256, policy and costs, state digests, seven implementation file byte digests, and each market receipt. Its top-level SHA-256 covers the canonical report payload. The fixture SHA-256 is `bbbfecaeabbb70d68ab3b513e575edf2da5cac1ba86c3ae7fa20cf509f477dbc`.

Implementation starts from repository commit `ccd4f7417da5263a2f3d66abbd20e0bbd6cf93f6`; the demo additions are identified by the review branch and the report's implementation digests. These hashes support reproducibility and change detection; they are not signatures or proof of genuine market observations.

## Interpretation boundary

Five selected adverse states prevent simulated submission after the recheck; the unchanged control is admitted. These hand-authored examples do not establish a detection rate or production performance.

The seventh case is intentionally unresolved by the guard: depth changes during the 20 ms gap after the final check/send. The guard has no access to that future state and still returns `EXECUTE_SIM`. Arrival data is evaluated only afterwards as a diagnostic; it cannot influence the earlier decision. Changes between the last observation and the check can likewise remain unseen.

There is no atomic binding to an exchange, reservation of liquidity, fill or P&L claim. Only best-level capacity is modeled; multi-level depth, partial fills, queue priority, instrument filters, balances and sequential leg execution are outside this fixture. The report remains `UNASSESSED_REPLAY_SOURCE` with `NONE_ADMISSION_ONLY` as its fill-model label.

For a follow-up technical review, the useful question is which public or synthetic exchange-state field and timestamp semantics should be included in a second fixture. Credentials and private strategy data are unnecessary.
