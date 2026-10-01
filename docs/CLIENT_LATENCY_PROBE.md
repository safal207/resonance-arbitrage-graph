# Opt-in Binance client-path latency probe

This is the first measurement slice, not a trading integration, exchange SLA test,
order-recovery test, or speedup claim. It leaves the existing HTTP helper, adapter,
quote validation, pre-trade policy, and trading decisions unchanged.

## Run

From an installed checkout, or with `PYTHONPATH=src`:

```sh
# Default: offline, synthetic data; three samples; no network.
python -m resonance_arbitrage_graph.latency_probe --output evidence/latency-fixture

# Controlled synthetic acquisition delay; not exchange/network performance.
python -m resonance_arbitrage_graph.latency_probe \
  --fixture-delay-ms 25 --output evidence/latency-delayed

# Explicit public-data-only smoke run; no keys, accounts, orders, or retries.
python -m resonance_arbitrage_graph.latency_probe \
  --live --samples 3 --interval 1 --timeout 3 --output evidence/latency-live

python -m pytest tests/test_latency_probe.py -q
```

Every output directory must be new. The live CLI requires at least one second
between successful polls. It stops on the first failure (including DNS failures,
timeouts, HTTP 418/429, invalid JSON, or adapter rejection). A failed live run
returns exit code 1 **after** writing its evidence. It does not produce successful
latency samples from failed requests. `completed_requested_samples` means all
requested attempts were made, not that they all succeeded; inspect counts/status.
The sample cap is 1001: at most 1000 metadata-cache-reused observations after the
first successful cold-metadata sample. This is a bounded smoke/measurement tool,
not a load generator.

## Integration and measurement boundaries

`MeasuredJSON` is injected through `BinanceBookTickerAdapter(fetch_json=...)`.
The probe sets `metadata_base_url` on its own adapter instance to the public-data
host. Both `exchangeInfo` and `bookTicker` are documented there. Defaults elsewhere
in the repository are unchanged. No other endpoints/hosts, extra query fields,
HTTP redirects, authentication, transport retries, or alternate-host fallbacks
are enabled by the built-in transport. An injectable opener/clock exists for
local tests; the public CLI does not accept arbitrary URLs or credentials.

| Field | What is measured |
| --- | --- |
| `open_to_headers_ns` | Local opener/context entry until response headers become available. Includes unresolved DNS/TCP/TLS/proxy/server components; not a wire-level TTFB claim. |
| `body_read_ns` | Response body read call, bounded by a size limit; declared Content-Length is checked when present. |
| `transport_to_body_ns` | Start of opener until the body read returns. Not pure exchange processing or one-way network latency. |
| `decode_json_ns` | UTF-8 decoding and JSON object parsing. Failed decode intervals are not mixed with successful intervals. |
| `request_elapsed_ns` | Instrumented fetch pipeline through success/error, before body hashing and evidence recording. |
| `adapter_total_ns` | Full instrumented adapter call; includes metadata work when requested and existing snapshot validation. |
| `adapter_other_ns` | Adapter total minus recorded request intervals. Includes local conversion/validation **and observer bookkeeping**. Not isolated verifier time. |
| `verifier_ns` | `null`: the verification engine is not measured by this slice. |
| `source_age_ms` | `null`: REST bookTicker does not provide an exchange publication timestamp. |

Intervals use `perf_counter_ns()`; wall-clock timestamps are for correlation only.
Integer nanoseconds do not promise nanosecond physical accuracy. Scheduling,
proxies, Python instrumentation, and measurement overhead remain in the result.
Runtime/clock properties, instrumentation/proxy environment variable *names*, and
hashes of the probe and five relevant source files are included. Secret values
are not included. Environment isolation and overhead subtraction are not claimed.
`--timeout` is urllib's socket timeout, **not a hard end-to-end deadline**.

Both adapter and per-endpoint summaries are separated into `metadata_requested`
and `metadata_cache_reused`, based on the requests actually issued. This is an
application metadata-cache distinction, not proof of DNS/TLS/connection warmth.
A failed metadata request does not make the next request warm. There is no cache
reset or policy change outside this probe instance.

Summary statistics are conditional on success; failures are counted and their
elapsed durations reported separately. Empirical nearest-rank p95 requires at
least 100 successful observations *within the same group*, and p99 requires 1000.
Smaller groups get `null`, not zero or invented percentiles. These are conservative
reporting thresholds, **not confidence guarantees**; serial correlation and
selection due to failures are not resolved by reaching those counts. A short
smoke run is not a service-level benchmark.

## Evidence and what it does not prove

Each run produces `report.json`, exact received bounded bodies in
`raw/<sha256>.bin`, and `sha256.json`. A failed/incomplete read that yields no body
has a null body reference. The response limit is 1 MiB plus one detection byte;
oversized or length-inconsistent bodies are rejected. Non-200, invalid UTF-8,
non-object JSON, non-finite JSON constants, and adapter-rejected data cannot
become successful adapter snapshots.

Hashes bind the saved bytes for integrity comparison. They do **not** authenticate
Binance, prove the recorder is honest, prove completeness, establish a signature,
or permit exact replay of live timings. Synthetic fixture runs are marked
`SYNTHETIC_FIXTURE`, separately from attempted `LIVE_PUBLIC_HTTP` runs. A live run
that fails DNS has no exchange response and must not be described as a measured
exchange latency. Snapshot `timestamp_class=client_observed` and null source
timestamps are preserved, never relabeled as exchange timestamps.

## Validation scope at preparation

Prepared against upstream `ccd4f7417da5263a2f3d66abbd20e0bbd6cf93f6`.
Local targeted tests use the actual upstream `binance.py`, `http.py`, `quotes.py`,
`model.py`, and `validation.py`; their Git blob hashes were checked byte-for-byte.
Because a full git checkout could not be downloaded in the preparation runtime,
these tests ran against a five-file dependency subset without the package's root
initializer. This is **not a full repository/packaging regression run**. The draft
must remain unmerged until repository CI and review are checked on its exact head.

Coverage includes controlled same-regime delay injection, metadata-cache behavior,
wall-clock reversal, open/read timeouts, DNS error separation, HTTP failure handling,
JSON failures and raw-body binding, size/truncation limits, unchanged adapter
validation, endpoint/credential/redirect restrictions, percentile suppression,
non-overwriting output, secret-free environment metadata, and input validation.

A next, separate slice can connect a verifier and a controlled order-recovery
simulation. This slice does not send orders, test idempotent execution, certify a
client system, claim profitable trading, or merge ContractGraph-QA/T-Trace logic.

## Primary references

- Python clocks: https://docs.python.org/3/library/time.html#time.perf_counter_ns
- Binance public-only endpoints: https://developers.binance.com/en/docs/products/spot/faqs/market_data_only
- Binance Spot market data: https://developers.binance.com/en/docs/catalog/core-trading-spot-trading/api/rest-api/market
