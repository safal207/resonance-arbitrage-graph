# Bounded quote staleness policy

This module separates **client observation age** from **exchange-published snapshot age**. It is intentionally fail-closed when the evidence cannot support a source-age claim.

## Why this exists

A fast HTTP response does not prove that the market data itself was freshly published. Conversely, a locally recent observation can still have unknown source age when the venue endpoint does not publish a timestamp for the complete snapshot.

The policy therefore has two independent caller-supplied bounds:

- `max_observation_age_ms`: maximum age since the client observed the snapshot.
- `max_source_age_ms`: optional maximum age since the exchange published the complete snapshot.

These values are test inputs / policy inputs. They are **not** trading recommendations, venue SLAs, or inferred safe thresholds.

## Verdicts

- `FRESH`: every requested bound is supported by the timestamp semantics and is within the supplied limit.
- `STALE`: at least one supported requested bound is exceeded.
- `UNKNOWN`: the requested source-age claim cannot be established, or a relevant timestamp is in the future relative to `now_ms`.

Boundary values are inclusive: age exactly equal to the configured maximum is `FRESH`; only age greater than the maximum is `STALE`.

## Timestamp semantics

`exchange_published` may be used for `max_source_age_ms` because its `source_timestamp_ms` describes publication of the complete snapshot.

`client_observed` has no exchange publication timestamp. If `max_source_age_ms` is requested, the result is `UNKNOWN` rather than pretending that receipt time is source time.

`client_observed_level_update` may contain an exchange timestamp for a price-level update, but that timestamp is **not** treated as publication time of the complete snapshot. A requested full-snapshot source-age check therefore returns `UNKNOWN`.

Future timestamps are also `UNKNOWN`; the policy does not clamp them to zero and call them fresh.

## Current Binance implication

The existing Binance `bookTicker` adapter records `timestamp_class="client_observed"` and `source_timestamp_ms=None`. Therefore:

- a client-observation-only policy can classify the local observation age;
- a policy that also requires exchange-published snapshot age must return `UNKNOWN` for this endpoint.

That is a deliberate evidence boundary, not a failure of Binance or a latency measurement.

## Example

```python
from resonance_arbitrage_graph.staleness import StalenessPolicy, assess_quote_staleness

assessment = assess_quote_staleness(
    snapshot,
    now_ms=now_ms,
    policy=StalenessPolicy(
        max_observation_age_ms=100,
        max_source_age_ms=100,
    ),
)
```

Do not choose those example values as production thresholds without a system-specific risk model.

## Non-claims

This policy does not prove one-way network latency, clock synchronization, profitable execution, order recovery correctness, or customer-system safety. It classifies only the timestamp evidence and explicit age bounds provided to it.
