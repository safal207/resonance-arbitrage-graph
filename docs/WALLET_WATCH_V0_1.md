# Wallet Watch v0.1

One public Ethereum address → USDC Transfer → RPC verification → local console
notification → durable SQLite history. This is a separate read-only module; it
does not change the arbitrage verifier or its paper-trading policy.

## Try the complete flow without an account

From the repository root, with Python 3.11 or later:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[test]"
python -m resonance_arbitrage_graph.wallet_watch_cli demo --db wallet-data/demo.sqlite3
python -m resonance_arbitrage_graph.wallet_watch_cli history --db wallet-data/demo.sqlite3
```

On Windows, activate with `.venv\Scripts\activate`.

The demo creates a **synthetic incoming transfer of 125.500000 USDC**, verifies
its fixture receipt/block, creates one console notification, closes/reopens the
database and processes the transaction again. The second pass must add zero
events and emit zero notifications. Running the demo again also keeps one
history event. Every fixture record and notification says `SYNTHETIC_FIXTURE`.
The addresses, hash and block numbers are invented test data; the explorer URL
in that fixture is not evidence of a real transaction.

An installed environment also exposes `resonance-wallet-watch` as a shorter
alias for `python -m resonance_arbitrage_graph.wallet_watch_cli`.

## Read one real transaction

Choose a public Ethereum address and a transaction hash involving that address.
No wallet connection, seed phrase, signing key or exchange credentials are used.

```bash
python -m resonance_arbitrage_graph.wallet_watch_cli transaction \
  --address 0xYOUR_PUBLIC_ETHEREUM_ADDRESS \
  --tx 0xTRANSACTION_HASH \
  --min-usdc 1 \
  --db wallet-data/live.sqlite3
```

The placeholders must be replaced by a 20-byte address and 32-byte hash.
Default endpoint: `https://ethereum-rpc.publicnode.com`. Availability, rate
limits and history access are provider-dependent. A provider supporting
`eth_chainId`, `eth_getBlockByNumber`, `eth_getLogs` and
`eth_getTransactionReceipt`, including the `finalized` block tag, is required.
If another HTTPS endpoint is needed, set `WALLET_RPC_URL` in the operator's
environment. Use the environment variable rather than command-line arguments
for URLs containing provider API credentials. Only the endpoint hostname is
retained in evidence; transport errors omit the URL.

Live RPC connectivity was unavailable in the authoring environment. The
included validation and CI demo establish the synthetic path only; they do
not establish successful collection of a real transfer. A successful live
check must preserve its actual transaction, blocks, receipt and origin.

## Watch an address and resume

```bash
python -m resonance_arbitrage_graph.wallet_watch_cli watch \
  --address 0xYOUR_PUBLIC_ETHEREUM_ADDRESS \
  --min-usdc 100 \
  --db wallet-data/live-watch.sqlite3
```

The first run scans the latest **50 finalized blocks**. It does not import the
wallet's full past history. Subsequent scans resume from the committed block
checkpoint, at most 50 blocks per iteration. Polling defaults to 60 seconds.
Finalization deliberately delays notification relative to initial inclusion.
`scan` performs a single iteration and exits. `watch` continues while the local
process is running. It is not a hosted service or a ChatGPT wallet automation.

For a bounded historical start, add `--start-block N` on the first run only.
Omit it on restart. Batch size can be set to 1–100 blocks. There is no silent
jump to the latest block when catching up. Large address histories may require
a suitable RPC plan and smaller batches.

The database is bound to one normalized address, Ethereum mainnet, USDC,
notification threshold and data origin. Changing these requires a separate
database. This prevents a test demo from mixing with live observations, or a
threshold change from silently relabeling prior notification decisions.

## What is checked before a notification

1. RPC chain ID is Ethereum mainnet (`1`).
2. The event comes from Circle's Ethereum USDC contract
   `0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48`.
3. It is a non-removed, canonically encoded ERC-20 `Transfer` event involving
   the watched address; integer token units are retained without float rounding.
4. The transaction receipt reports success and contains exactly one matching
   log at that log index, with matching transaction/block identity and amount.
5. The block agrees with the provider's canonical block at that height and is
   at or below the provider's finalized boundary.
6. The finalized view and scan boundary have not changed during collection.
7. Previously stored transfer identities have not acquired conflicting facts.

Incoming, outgoing and self-transfers are distinguished. The amount is USDC
token units, **not a fetched USD valuation**. A transfer is not classified as a
purchase, sale, arbitrage opportunity or an indication of its owner's intent.
No wallet ownership or entity attribution is inferred.

The result label is `RPC_CONSISTENT_FINALIZED`: agreement among one provider's
responses. This is **not** independent consensus verification, a cryptographic
receipt-inclusion proof, a guarantee that the provider returned every log, or
a guarantee of source authenticity. `LIVE_RPC` describes the acquisition path,
not an independent certification of the provider. The saved SHA-256 detects
changes relative to the saved packet; it is not an externally signed timestamp
and cannot defeat someone rewriting both the data and digest.

## History and notifications

```bash
python -m resonance_arbitrage_graph.wallet_watch_cli history \
  --db wallet-data/live-watch.sqlite3
python -m resonance_arbitrage_graph.wallet_watch_cli notifications \
  --db wallet-data/live-watch.sqlite3
```

History includes the raw selected log, receipt, block/finalized evidence,
observation time, source hostname, exact amount, direction, transaction link,
stable event ID, digest and notification state. Reading history rechecks the
digest and reproduces the event from the evidence. Events below the threshold
remain in history without creating an outbox notification.

Event identity is `chain:token:transaction_hash:log_index`, with the address
bound to the database. Retries and self-transfers returned by both filters
produce one history entry. A scan commits all verified events, pending outbox
records and its block checkpoint in one SQLite transaction. Failed collection
or verification leaves the previous checkpoint in place.

The delivery sink in this version is **local stdout**. `console_emitted` means
the write/flush completed, not that a person read the message. Nothing is sent
to email, Telegram or a webhook. An interrupted/failed output remains pending.
A crash after output but before acknowledgment can repeat the same event ID:
delivery is **at least once**, not exactly once. Use one console consumer per
database; a future external receiver must deduplicate by event ID.

RPC or integrity errors exit with code 2. `watch` stops on an error so the
operator can inspect the cause and restart from the saved cursor. A changed
finalized checkpoint is an explicit manual-review stop, not an automatically
rewritten history. Ctrl-C exits with code 130 after committed work is preserved.

Local databases belong under ignored `wallet-data/`. Do not commit an operator's
watchlist, database or provider credentials. The provided GitHub Actions demo
uploads only synthetic JSON evidence.

## Проверка для Алексея

- Команда `demo` показывает весь сценарий без регистрации и реальных средств.
- `history` показывает сохранённое событие и состояние уведомления.
- Для своих данных нужны публичный Ethereum-адрес и доступный RPC-провайдер.
- Эта версия сообщает в локальной консоли. Доставка уведомлений на телефон
  и постоянный хостинг — отдельный следующий шаг.
- Для недельного пилота измеряем пропуски относительно независимой выборки,
  дубли, задержку до уведомления и оценку полезности оператором. Точность
  обнаружения и готовность платить пока не измерены.

## Primary references

- [Ethereum JSON-RPC](https://ethereum.org/developers/docs/apis/json-rpc/)
- [ERC-20 Transfer event](https://eips.ethereum.org/EIPS/eip-20)
- [Circle USDC contract addresses](https://developers.circle.com/stablecoins/usdc-contract-addresses)

## Verification

```bash
python -m pytest tests/test_wallet_watch.py
python -m pytest
```

Tests exercise the full CLI demo, persistence/restart, failed output recovery,
canonical transfer decoding, receipt/block/finality disagreement, removed logs,
wrong chain/token/address, exact uint256 amounts, atomic checkpoints, conflicting
replays, altered evidence, threshold/origin binding and read-only RPC transport.
