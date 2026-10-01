# Fail-closed decision validity gate

`decision_validity.py` consumes a completed `StalenessAssessment` and decides only whether downstream non-execution checks may continue.

## Mapping

| Staleness evidence | Decision validity | Meaning |
| --- | --- | --- |
| `FRESH` | `CONTINUE_CHECKS` | Freshness evidence passed; other checks may run. |
| `STALE` | `BLOCK` | The quote input is outside the supplied freshness policy. |
| `UNKNOWN` | `HOLD` | Evidence is insufficient or ambiguous; do not treat it as fresh. |

Every `DecisionValidityAssessment` has `execution_authorized=false`. Construction with `true` is rejected. This gate cannot authorize an order.

## Why this exists

The product chain is intentionally separated:

`client-path latency -> timestamp evidence -> staleness verdict -> decision-input validity -> later risk/recovery checks`

A low latency number is not itself a freshness proof. A `FRESH` staleness verdict is not itself a profitable or safe trade. `CONTINUE_CHECKS` means only that this one evidence gate does not block the next bounded check.

## Non-claims

This module does not evaluate profitability, balances, account permissions, order state, idempotence, settlement, market impact, customer risk limits, or execution safety. It is not yet wired into the latency CLI report.
