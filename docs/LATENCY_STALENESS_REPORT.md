# Latency + staleness evidence report

The latency probe can optionally attach a bounded staleness assessment to every successful quote snapshot. This is an evidence classification, not a trading recommendation.

## Opt-in policy

No staleness threshold is invented by the probe. Without a caller-supplied observation-age bound, the report contains `staleness: null` for each attempt and `staleness_policy: null` in config.

Enable local observation-age classification explicitly:

```sh
PYTHONPATH=src python -m resonance_arbitrage_graph.latency_probe \
  --max-observation-age-ms 100 \
  --output evidence/latency-with-observation-policy
```

Require both local observation age and exchange-published snapshot age:

```sh
PYTHONPATH=src python -m resonance_arbitrage_graph.latency_probe \
  --max-observation-age-ms 100 \
  --max-source-age-ms 100 \
  --output evidence/latency-with-source-policy
```

The values above are examples only. They are not venue SLAs or safe production defaults.

## Current Binance behavior

The current Binance `bookTicker` adapter records `timestamp_class="client_observed"` and does not claim an exchange publication timestamp for the complete snapshot. Therefore:

- an observation-only policy may return `FRESH` or `STALE` from the local observation time;
- a policy that requires `max_source_age_ms` returns `UNKNOWN` with `SOURCE_PUBLICATION_TIMESTAMP_UNAVAILABLE` while the observation itself is within its bound.

A fast client-path measurement is never substituted for exchange source age.

## Measurement boundary

Staleness classification runs only after the adapter timing interval has closed. Its computation is not included in `adapter_total_ns`.

The report schema is `resonance-client-latency/v2`. Each successful attempt may include:

```json
{
  "staleness": {
    "verdict": "UNKNOWN",
    "observation_age_ms": 4,
    "source_age_ms": null,
    "reasons": [
      "CLIENT_OBSERVATION_WITHIN_BOUND",
      "SOURCE_PUBLICATION_TIMESTAMP_UNAVAILABLE"
    ]
  }
}
```

The summary adds `staleness_by_verdict` counts. The evidence bundle still hashes `report.json` and bounded raw response bodies as before.

## Non-claims

This integration does not prove one-way network latency, clock synchronization, exchange publication age when no such timestamp is provided, order recovery correctness, profitable execution, or customer-system safety.
