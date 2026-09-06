# PR #85 — attempted live scan continuation

[Download evidence archive](resonance-wallet-resume-proof-pr85.zip) · [SHA-256 checksums](SHA256SUMS) · [Offline verification result](verification.json)

**Result: INCOMPLETE.** Neither attempt completed the scan of block 25,919,604.
Both stopped before saving any scan progress. The original database, event and
notification acknowledgement remained unchanged. Zero output on these failed
attempts is **not** evidence that the target block contains no relevant transfers.

Tested source: `e2d644155b587da89b12116a9b94150c6e5d4837` (clean checkout).
Single provider: `ethereum-rpc.publicnode.com`; acquisition: `LIVE_RPC`.

The starting database is a byte-identical copy of the
[previous published live proof](https://github.com/safal207/resonance-arbitrage-graph/blob/dc445bfac231ba6a3bcaac9c6388805d163c3c75/docs/evidence/wallet-watch-pr85/README.md).
Its successful one-transfer result is separate from this incomplete continuation.
That earlier proof covered an existing 300.000000 USDC transfer at block 25,919,603,
not a successful resumed scan into the next block.

| Observation | Attempt 001 | Attempt 002 |
| --- | --- | --- |
| Time (UTC, 2026-09-06) | 19:02:16–19:03:00 | 19:05:18–19:06:02 |
| Fresh CLI processes | history, scan | history, scan |
| Requested scan range | 25,919,604 only | 25,919,604 only |
| Scan exit code | 2 | 2 |
| Successful RPC responses before failure | 4 | 4 |
| Failed request | outgoing `eth_getLogs` | outgoing `eth_getLogs` |
| Scan stdout | empty | empty |
| Checkpoint after exit | 25,919,603 | 25,919,603 |
| History events / pending notifications | 1 / 0 | 1 / 0 |
| Database bytes and logical state | unchanged | unchanged |

Each scan ran in a new process on its own copy of the same previously saved
database, using `--batch-size 1` and **omitting `--start-block`**. Both attempts
reached the expected next-block log query. Neither reached the incoming log query,
the final consistency checks, the checkpoint commit, or the planned post-advance
transaction replay. All attempts are retained, including their failures.

## Diagnostic and its limits

At 19:06:46–19:06:55 UTC, a separate read-only diagnostic repeated the identical
failed JSON-RPC request through the same endpoint. It received HTTP **403** and
JSON-RPC error **-32602**. The captured body says:

> Archive requests require a personal token. Get one at: https://www.allnodes.com/publicnode

This diagnostic records the status and body. The original capture wrapper records
only `HTTPError` for each failed scan request; their individual HTTP status/body
were not retained. The diagnostic identifies an access requirement for the repeated
request, but does not establish a network-wide outage, a retention-window rule, or
the correctness/completeness of any unreturned logs. No alternative provider or
credential was used.

## Verify the retained evidence offline

Use Python 3 and a clean source checkout at the exact SHA above. From this extracted
bundle, run (replace `/path/to/source` with that checkout):

```bash
python verify_bundle.py --repo /path/to/source --bundle .
```

The verifier checks the payload inventory and SHA-256 hashes, source identity,
SQLite integrity, byte-identical before/after databases, retained event evidence,
RPC response/request bindings and the failed next-block query. It makes no network
requests. `bundle_integrity: PASS` means the retained package is consistent;
`live_resume_status` must remain **INCOMPLETE**.

The original baseline archive SHA-256 is
`6c6122bd85437f598629b3dfeb1f7599013b2586dac7d969963f090fc6903e7f`.
The baseline scan database SHA-256 is
`8e43bfff660fb11fa132865c9da2264761699e7ed7c79c8f6a4dd8db24e1e2a7`.
Both original files were rechecked after the attempts and left unchanged.

## Reproduce the bounded attempt

Extract the baseline archive linked above into `/path/to/baseline`. Use a new output
directory and the same clean source checkout:

```bash
python attempt-002/run_wallet_resume_proof.py \
  --repo /path/to/source \
  --baseline /path/to/baseline \
  --out /path/to/new-attempt
```

The runner copies the database before starting, retains every command's stdout,
stderr and RPC capture, and reports PASS only if the whole scenario completes.
It uses the original capture helper unchanged, which pins the anonymous public
endpoint and ignores `WALLET_RPC_URL`. A later reproduction can have a different
transport outcome; it must be recorded as a new attempt.

To continue this historical-block experiment, configure authorized archive access
to the same provider. The source CLI already supports a credential-bearing endpoint
through `WALLET_RPC_URL`. A future capture must explicitly use that configuration,
retain only its hostname and distinguish it from this anonymous-endpoint attempt;
changing the environment alone does not change this archived runner.

## Claim boundaries

This package supports preservation of local state after two observed pre-commit
HTTP failures and selection of the next block from the saved cursor. It does not
establish successful checkpoint advancement, a clean empty-block scan, post-advance
deduplication, unattended recovery, continuous monitoring, independent network
verification, provider completeness or exactly-once delivery. Existing notification
acknowledgements represent local stdout only. Trading, profit and ownership are not
evaluated. The PR source was not changed by these attempts.
