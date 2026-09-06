# PR #85 — recent two-block scan continuation

[Download evidence archive](resonance-wallet-recent-resume-pr85.zip) · [SHA-256 checksums](SHA256SUMS) · [Offline verification result](verification.json)

**PASS for this bounded live scenario:** one initial Ethereum USDC transfer was
verified and saved; a new CLI process resumed from the saved cursor into the next
block; a further process replayed the original transaction without a duplicate
event or console notification. History and the advanced checkpoint persisted.

Tested source: `e2d644155b587da89b12116a9b94150c6e5d4837`, clean throughout.
Provider: `ethereum-rpc.publicnode.com`, anonymous public endpoint, no credential or
provider change. Acquisition: `LIVE_RPC`; verification: `RPC_CONSISTENT_FINALIZED`.

**This is a new database and a newly selected public address.** It does not resume
the earlier 300 USDC database at block 25,919,603. That historical continuation
remains [INCOMPLETE with its captured archive-access error](https://github.com/safal207/resonance-arbitrage-graph/blob/4cc66497c2e32221d3a726cd78b247cda57873b1/docs/evidence/wallet-watch-pr85/resume-20260906/README.md).
The earlier archive and scan database were rechecked and left unchanged; see
`prior-evidence-unchanged.json`.

| Step | Observed result |
| --- | --- |
| Initial one-block scan | Block 25,920,399; 1 event, 1 stdout notification |
| Transfer | 100.000000 USDC; incoming; log index 13 |
| New-process resume | Block 25,920,400; 0 new events, 0 stdout notifications |
| Cursor | 25,920,399 → 25,920,400 |
| Original transaction replay after resume | 0 new events, 0 stdout notifications |
| Final history and pending outbox | 1 retained event, 0 pending notifications |
| Process outcomes | All 7 fresh CLI processes exited 0 |

Transaction:
[`0xbac280925b5c6241595ff6b11f539cd1d529d932e917a510731f88dd8f068ab4`](https://etherscan.io/tx/0xbac280925b5c6241595ff6b11f539cd1d529d932e917a510731f88dd8f068ab4).
The explorer link is a convenience, not a second verification source.

Watched public address: `0xf740669fbcc0242f0302bdd9a3c6a01ddafb1bc4`.
No ownership, intent or identity is inferred.

## Selection and observation

The harness read the provider's finalized boundary F = 25,920,400. It queried USDC
logs in the single preceding block F−1, choosing the lowest-log-index transfer of
at least 1 USDC whose nonzero recipient occurred once in that block's returned USDC
logs. The choice used no next-block log data. Both target blocks were already
finalized according to this provider when the experiment began.

The first scan started a new database at F−1 with `--start-block` and a batch size
of one. After that process exited, the database was copied to the retained
`scan.before-resume.sqlite3`. A new scan process used the same working database
with `--batch-size 1` and **without `--start-block`**. It requested only F, checked
the previous checkpoint and current boundary, then saved the advanced cursor.
There was no manual cursor edit, skipped gap inside this two-block scenario,
fabricated transfer or transaction submission.

The original event packet and outbox acknowledgement are logically byte-for-byte
unchanged in the before/after snapshots. After the resumed scan, transaction replay
and pending-output drain, the entire logical database state matched the state
immediately after resume. The retained before/after database files naturally differ
because the checkpoint advanced.

## Evidence and offline reproduction

The bundle contains raw RPC response bytes, corresponding request records,
per-command stdout/stderr, before/after databases, state snapshots, selection rule,
source-file digests, timestamps, runner and an offline verifier. The capture helper
is unchanged from the previous published live-proof package and wraps only urllib
response reads; it does not change the request or response bytes.

Use Python 3 and a clean checkout at the source SHA above. From the extracted
bundle, substitute the checkout path and run:

```bash
python verify_recent_resume.py --repo /path/to/source --bundle .
```

The verifier checks the complete SHA-256 manifest, SQLite/event-evidence integrity,
request/response bindings, scan ranges, durable state and outputs. It then runs the
original CLI in three new subprocesses against the captured RPC bytes: initial
scan, resumed scan and transaction replay. Every RPC read is intercepted; no network
request is made. Replay databases are temporary and are not published as live data.

For offline comparisons, wall-clock `observed_at`, row creation and acknowledgement
timestamps can differ. The comparison omits those values and their dependent output
packet digest, while retaining packet contents, event projections, acknowledgement
state, checkpoint and event/output counts. Actual packet digests are independently
recomputed in both the live evidence and temporary replay database. Transaction
replay must leave the complete temporary database state unchanged.

To run a **new** bounded live experiment using the same selection rule:

```bash
python run_recent_resume_proof.py \
  --repo /path/to/source \
  --capture-helper ./capture_cli.py \
  --out /path/to/new-empty-attempt
```

This selects blocks from the provider's current finalized boundary; it does not
request these now-historical blocks. It uses a new database and retains failure if
no qualifying transfer is available or the provider rejects a request. The capture
helper pins the public endpoint and ignores `WALLET_RPC_URL`.

## Limits

This establishes one successful recent-block continuation after an ordinary process
exit/restart, plus ordinary transaction replay on the same database. It does not
establish continuous monitoring, automatic retry after access failure, crash/power-loss
recovery, arrival-detection latency or an archive-access capability.

The next block returned no matching logs through this provider. That observation
does not independently prove source completeness or the absence of relevant network
events. All transfer, receipt, canonical-block and finality checks use one RPC
provider; this is not independent inclusion or consensus verification.

Notification counts concern local stdout and acknowledgements, not phone delivery
or human receipt. An output/acknowledgement crash can still repeat the same event ID;
exactly-once delivery is not claimed. Trading, profitability, release approval and
deployment are outside this experiment.
