# PR #85: bounded live wallet-watch evidence

Capture date: **2026-09-06**, 17:03:47–17:08:04 UTC.
Tested source: [e2d644155b587da89b12116a9b94150c6e5d4837](https://github.com/safal207/resonance-arbitrage-graph/commit/e2d644155b587da89b12116a9b94150c6e5d4837).
Target: [PR #85](https://github.com/safal207/resonance-arbitrage-graph/pull/85).

**PASS for one existing finalized transfer through one provider.** This evidence commit publishes the completed capture; it is a separate identity from the tested source revision.

## Download and inspect

- [Original evidence archive](resonance-wallet-live-proof-pr85.zip)
- [Measured results](result.json)
- [Archive SHA-256](SHA256SUMS)

Archive: 188,463 bytes; SHA-256:
`6c6122bd85437f598629b3dfeb1f7599013b2586dac7d969963f090fc6903e7f`.

The archive contains the report, capture and offline-verification helpers, 30 exact JSON-RPC response bodies with paired request records, CLI output, two sample SQLite databases, revision provenance, and a manifest covering 88 payload files (plus the manifest itself). These are public sample-transfer databases, not an operator's private wallet database or watchlist. No credentials or signing keys were used.

The archive is preserved byte-for-byte. Its report describes the earlier capture-time state, including that no PR update had yet been made. This publication note records the subsequent evidence-publication step.

## Specimen

Provider: `ethereum-rpc.publicnode.com` only. Chain ID: `0x1`.
Contract: `0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48`.
Amount: **300.000000 USDC** (`300000000` integer token units).
Block: **25919603**; log index: **5**.
Transaction: [0xbe18af1609eba93e7e25d18e46c5d6662e15ee92ac6f029864e5feede515cf35](https://etherscan.io/tx/0xbe18af1609eba93e7e25d18e46c5d6662e15ee92ac6f029864e5feede515cf35).
The explorer link is a convenience link, not a second verification source.

The sample was selected from one provider-returned finalized block: first qualifying log of at least 1 USDC whose nonzero recipient appeared in exactly one returned transfer. No wallet ownership or intent is inferred.

| Check | Observed result |
| --- | --- |
| Fresh transaction lookup | 1 event, 1 console notification |
| Fresh one-block scan in a separate database | Same event, 1 notification |
| Ordinary process restart and replay in each database | 0 new events, 0 notifications |
| Saved history and scan checkpoint | Retained and unchanged on replay |
| Pending notification drain | 0 output records |
| Offline verification | 88 files and 30 RPC responses checked; event projection PASS |

There were **2 initial console outputs across 2 isolated fresh databases**, referring to **1 distinct event ID**. There were no additional outputs on same-database replay. This is not an exactly-once delivery result.

## Reproduce

Extract the archive. Use Python 3.11+ and a checkout of the tested source revision:

```bash
python wallet-live-proof-85/verify_bundle.py \
  --repo /absolute/path/to/pinned-source \
  --bundle /absolute/path/to/wallet-live-proof-85
```

The offline verifier checks saved bytes, source-file digests, paired RPC responses, event projections, and replay output counts. It makes no network calls. The archive report also contains commands for a live repeat of this exact specimen.

## Boundaries retained

- `LIVE_RPC` identifies acquisition; `RPC_CONSISTENT_FINALIZED` means agreement among one provider's responses.
- No independent consensus, cryptographic inclusion, provider authenticity or completeness proof.
- No continuous-watch, arrival-detection, latency, hosted-service, mobile/email/Telegram delivery or human-receipt claim.
- Only ordinary process restart/replay was observed. Output/acknowledgment crash delivery remains **at least once**.
- No signing, transfers initiated by this test, orders, trading signals, ownership attribution, arbitrage execution, USD valuation or profitability claim.
- Synthetic CI remains synthetic. This capture does not assert a new full test-suite run, review approval, merge or deployment.
- SHA-256 checks establish byte identity relative to retained artifacts, not source truth or an externally signed timestamp.
