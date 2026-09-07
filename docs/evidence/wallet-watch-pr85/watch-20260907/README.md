# Bounded live watch attempt, PR #85 — INCOMPLETE

Observed on 2026-09-07, 12:19:15–12:20:49 UTC. Tested source commit: `e2d644155b587da89b12116a9b94150c6e5d4837`. The tracked checkout was clean before and after the attempt. Source-file hashes and the original command are in `provenance.json` and `commands.json`.

The intended scenario was two bounded `watch` processes sharing a new database: finish two iterations, interrupt during the polling interval, restart without `--start-block`, then process a block beyond the provider's initially finalized boundary. That scenario **did not complete**.

| Observation | Actual result |
| --- | --- |
| Public RPC provider | `ethereum-rpc.publicnode.com`, one provider |
| Initial finalized boundary reported by provider | 25925370 |
| First requested scan block | 25925369 |
| Successful captured RPC responses | 9: discovery 3, watch 6 |
| Failed RPC requests | 1, `eth_getBlockByNumber`, captured exception class `URLError` |
| Live watch processes / completed iterations | 1 / 0 |
| CLI exit code | 2 |
| Stored events / console notifications / outbox rows | 0 / 0 / 0 |
| Checkpoint | Not created; number and hash are null |
| Planned controlled interruption, restart and newly finalized progress | Not reached |

Discovery selected one USDC log as a candidate. Its identifiers are retained in `selection.json`; it is **not a verified or saved transfer in this attempt**. The scan obtained the candidate's receipt, then failed on a block-header request before committing the scan. Zero saved events does not mean that the scanned block had no transfers.

The execution tool reported: `network approval was cancelled before a decision was returned`. The exact tool message is retained in `runtime-observation.json`. Separately, the capture wrapper recorded `URLError`, and the CLI emitted its redacted RPC failure message. No underlying URL-error reason or HTTP failure status/body was captured. These records do not diagnose a remote-provider defect or establish the archive-token restriction seen in an older, separate experiment. The runtime message reports cancellation before a decision, not an approval rejection. No further live attempt was made after this observation.

The fresh SQLite database passes its integrity check and contains only the bound configuration. It had no earlier checkpoint or events to preserve. The failed partial scan was not committed as completed. The included offline verifier replays the six successful watch responses, injects the recorded exception class at the seventh matching request, and compares the exit code, stdout, stderr and complete logical database state. It also checks all captured RPC byte digests, payload inventory and pinned source bytes. This can validate the recorded abort path; it cannot establish successful continuous monitoring or reproduce the external approval system.

`result.json` is the original harness verdict. `assessment.json` distinguishes measured counts from the unexecuted plan. `provenance.json` describes the intended controlled stop; `commands.json` records the actual exit 2 and that the stop condition was never reached. The earlier local preflight failed before RPC or watch execution because an old helper path was absent; `preflight-attempt-001.json` preserves that fact. The live attempt used the identical published helper recovered locally, with SHA-256 checked before launch.

## Offline reproduction

Use a clean checkout of the source commit above, Python 3.12, and the extracted archive directory. The verifier uses local captures only and blocks socket connections during CLI replay:

```sh
python -B /path/to/bundle/verify_incomplete_watch.py --repo /path/to/source-checkout --bundle /path/to/bundle
```

Expected: offline verification `PASS`, with `live_scenario_status: INCOMPLETE`, 9 captured responses, 1 failed request, 1 offline CLI execution, exit 2, zero completed iterations/events/notifications, and a null checkpoint. The response bytes are real captures; the final exception class is injected for replay. Its original reason was not recorded. No polling sleep or successful loop is replayed.

`run_bounded_watch_proof.py` and `capture_cli.py` retain the live harness for a later authorized attempt. `verify_bounded_watch.py` was prepared for a successful two-process capture and was **not executed** on this incomplete attempt; it requires a live PASS and must not be used to upgrade this result. Offline verification output and the archive checksum are published alongside the archive, outside its payload manifest.

## Scope and next step

The [earlier new-database two-block scan/resume PASS](https://github.com/safal207/resonance-arbitrage-graph/blob/34e99b59424924a50f5e35966bfd531d16eb1e2b/docs/evidence/wallet-watch-pr85/recent-resume-20260906/README.md) remains a separate bounded result. The earlier archival continuation remains INCOMPLETE. This attempt establishes neither successful watch-loop progress nor restart behavior. Arrival-detection latency, uninterrupted operation, independent network verification, provider completeness, exactly-once delivery and human receipt remain unestablished. No trade execution or profitability claim follows.

Minimal next step: repeat the same bounded watch scenario once the execution environment permits RPC access, retaining a new database and evidence directory. Tested source and PR head remain unchanged. The PR remains draft.

## Published package

[Download archive](resonance-wallet-watch-incomplete-pr85.zip) · [Offline verification](verification.json) · [Checksums](SHA256SUMS)

The extracted archive passed offline verification: 35 payload files, 9 successful captured RPC responses and 1 failed request; the one CLI replay ended with exit 2 and the same null checkpoint and empty event/outbox tables. **The live scenario remains INCOMPLETE.**

Archive: 59158 bytes. SHA-256: `a40aaa8a603e52ac8de79bef5e1c5a5bc3d8e3fff145355c68150680d9be7861`.
