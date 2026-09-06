"""Read-only Ethereum/USDC transfer monitoring with a durable local outbox.

Verification is consistency checking against one RPC provider's canonical and
finalized views, not a cryptographic inclusion proof or an ownership assertion.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import sqlite3
import time
from typing import Any, Callable
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

USDC = "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
DEFAULT_RPC = "https://ethereum-rpc.publicnode.com"
READ_METHODS = frozenset({"eth_chainId", "eth_getBlockByNumber", "eth_getLogs", "eth_getTransactionReceipt"})


class WatchError(ValueError):
    """Incomplete, inconsistent or unavailable evidence; never a clean scan."""


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def hex_data(value: Any, size: int) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"0x[0-9a-fA-F]{%d}" % (size * 2), value):
        raise WatchError(f"Expected {size}-byte hex data")
    return value.lower()


def quantity(value: Any) -> int:
    if not isinstance(value, str) or not re.fullmatch(r"0x(?:0|[1-9a-fA-F][0-9a-fA-F]*)", value):
        raise WatchError("Invalid RPC quantity")
    return int(value, 16)


def usdc_units(value: str) -> int:
    if not re.fullmatch(r"[0-9]+(?:\.[0-9]{1,6})?", value):
        raise WatchError("USDC amount must be non-negative with at most six decimal places")
    whole, _, fraction = value.partition(".")
    result = int(whole) * 1_000_000 + int(fraction.ljust(6, "0"))
    if result >= 2**256:
        raise WatchError("USDC amount exceeds uint256")
    return result


def format_usdc(units: int) -> str:
    whole, fraction = divmod(units, 1_000_000)
    return f"{whole}.{fraction:06d}"


class Rpc:
    origin = "LIVE_RPC"

    def __init__(self, url: str = DEFAULT_RPC, *, timeout: float = 15.0) -> None:
        parts = urlsplit(url)
        if parts.scheme != "https" or not parts.hostname or parts.username or parts.password or parts.fragment:
            raise WatchError("Use an HTTPS RPC URL without userinfo or fragment")
        self.url = url
        self.source = parts.hostname  # Never persist API keys in paths or queries.
        self.timeout = timeout
        self.sequence = 0

    def call(self, method: str, params: list[Any]) -> Any:
        if method not in READ_METHODS:
            raise WatchError("Only the four read-only wallet-watch RPC methods are allowed")
        self.sequence += 1
        request = Request(self.url, data=canonical({"jsonrpc": "2.0", "id": self.sequence,
                          "method": method, "params": params}).encode(),
                          headers={"Content-Type": "application/json", "User-Agent": "resonance-wallet-watch/0.1"})
        try:
            with urlopen(request, timeout=self.timeout) as response:
                raw = response.read(4_000_001)
            if len(raw) > 4_000_000:
                raise WatchError("RPC response exceeds bounded response size")
            body = json.loads(raw)
        except Exception:
            # Underlying exceptions can contain credentials embedded in an RPC URL.
            raise WatchError(f"RPC transport/JSON failure for {method}; checkpoint retained") from None
        if (not isinstance(body, dict) or body.get("jsonrpc") != "2.0"
                or type(body.get("id")) is not int or body["id"] != self.sequence
                or "error" in body or "result" not in body):
            raise WatchError(f"Invalid RPC response for {method}; checkpoint retained")
        return body["result"]


def _block(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise WatchError("Missing block; finalized support is required")
    quantity(value.get("number"))
    quantity(value.get("timestamp"))
    hex_data(value.get("hash"), 32)
    # Keep only the header fields used for consistency checking.
    return {"number": value["number"], "timestamp": value["timestamp"], "hash": value["hash"]}


def _topic_address(value: Any) -> str:
    topic = hex_data(value, 32)
    if topic[2:26] != "0" * 24:
        raise WatchError("Non-canonical address topic")
    return "0x" + topic[26:]


def decode_log(log: Any) -> dict[str, Any]:
    if not isinstance(log, dict) or log.get("removed") is not False:
        raise WatchError("Missing or removed transfer log")
    if hex_data(log.get("address"), 20) != USDC:
        raise WatchError("Unexpected token contract")
    topics = log.get("topics")
    if not isinstance(topics, list) or len(topics) != 3 or hex_data(topics[0], 32) != TRANSFER:
        raise WatchError("Not a canonical ERC-20 Transfer event")
    return {
        "tx_hash": hex_data(log.get("transactionHash"), 32),
        "log_index": quantity(log.get("logIndex")),
        "block_number": quantity(log.get("blockNumber")),
        "block_hash": hex_data(log.get("blockHash"), 32),
        "from_address": _topic_address(topics[1]),
        "to_address": _topic_address(topics[2]),
        "amount_units": str(int(hex_data(log.get("data"), 32), 16)),
    }


def verify_evidence(evidence: dict[str, Any], address: str) -> dict[str, Any]:
    """Recompute the event projection from the retained RPC evidence."""
    address = hex_data(address, 20)
    if quantity(evidence.get("chain_id")) != 1:
        raise WatchError("Ethereum mainnet (chain ID 1) is required")
    log = decode_log(evidence.get("log"))
    if address not in (log["from_address"], log["to_address"]):
        raise WatchError("Transfer does not involve the watched address")
    receipt = evidence.get("receipt")
    if not isinstance(receipt, dict) or receipt.get("status") != "0x1":
        raise WatchError("Missing or unsuccessful transaction receipt")
    if (hex_data(receipt.get("transactionHash"), 32) != log["tx_hash"]
            or quantity(receipt.get("blockNumber")) != log["block_number"]
            or hex_data(receipt.get("blockHash"), 32) != log["block_hash"]):
        raise WatchError("Receipt and transfer disagree")
    receipt_logs = receipt.get("logs")
    if not isinstance(receipt_logs, list):
        raise WatchError("Receipt logs are missing")
    matches = [item for item in receipt_logs if isinstance(item, dict)
               and item.get("logIndex") == evidence["log"]["logIndex"]]
    if len(matches) != 1 or decode_log(matches[0]) != log:
        raise WatchError("Transfer is not uniquely present in the receipt")
    block = _block(evidence.get("block"))
    finalized = _block(evidence.get("finalized"))
    if (quantity(block["number"]) != log["block_number"]
            or hex_data(block["hash"], 32) != log["block_hash"]):
        raise WatchError("Canonical block and receipt disagree")
    if quantity(finalized["number"]) < log["block_number"]:
        raise WatchError("Transfer has not reached the RPC finalized boundary")
    if quantity(finalized["number"]) == log["block_number"] and finalized["hash"].lower() != log["block_hash"]:
        raise WatchError("Finalized block hash disagrees")
    if quantity(block["timestamp"]) > quantity(finalized["timestamp"]):
        raise WatchError("Block timestamps disagree")
    direction = "self" if log["from_address"] == log["to_address"] else (
        "incoming" if address == log["to_address"] else "outgoing")
    return {**log, "event_id": f"1:{USDC}:{log['tx_hash']}:{log['log_index']}",
            "watched_address": address, "direction": direction, "token": "USDC", "decimals": 6,
            "amount": format_usdc(int(log["amount_units"])),
            "block_timestamp": quantity(block["timestamp"]),
            "verification": "RPC_CONSISTENT_FINALIZED",
            "transaction_url": f"https://etherscan.io/tx/{log['tx_hash']}"}


class History:
    def __init__(self, path: Path | str) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(path, timeout=5)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA foreign_keys=ON")
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS state (id INTEGER PRIMARY KEY CHECK(id=1), config TEXT NOT NULL,
                cursor_number INTEGER, cursor_hash TEXT);
            CREATE TABLE IF NOT EXISTS events (event_id TEXT PRIMARY KEY, packet TEXT NOT NULL,
                sha256 TEXT NOT NULL, created_at INTEGER NOT NULL);
            CREATE TABLE IF NOT EXISTS outbox (event_id TEXT PRIMARY KEY REFERENCES events(event_id),
                emitted_at INTEGER);
        """)

    def close(self) -> None:
        self.db.close()

    def bind(self, address: str, origin: str, minimum: int) -> None:
        config = canonical({"schema": "wallet-watch/0.1", "chain_id": 1, "token": USDC,
                            "address": hex_data(address, 20), "origin": origin, "minimum_units": str(minimum)})
        with self.db:
            self.db.execute("INSERT OR IGNORE INTO state(id,config) VALUES(1,?)", (config,))
            if self.db.execute("SELECT config FROM state WHERE id=1").fetchone()[0] != config:
                raise WatchError("Database belongs to another address, origin or threshold; use a separate database")

    def checkpoint(self) -> tuple[int, str] | None:
        row = self.db.execute("SELECT cursor_number,cursor_hash FROM state WHERE id=1").fetchone()
        return (row[0], row[1]) if row and row[0] is not None else None

    def save(self, packets: list[dict[str, Any]], *, minimum: int,
             checkpoint: tuple[int, str] | None = None, expected: tuple[int, str] | None = None) -> int:
        added = 0
        try:
            self.db.execute("BEGIN IMMEDIATE")
            if checkpoint is not None and self.checkpoint() != expected:
                raise WatchError("Another scan advanced this database; retry from its current checkpoint")
            for packet in packets:
                event = packet["event"]
                if verify_evidence(packet["evidence"], event["watched_address"]) != event:
                    raise WatchError("Event does not reproduce from evidence")
                prior = self.db.execute("SELECT packet,sha256 FROM events WHERE event_id=?", (event["event_id"],)).fetchone()
                if prior:
                    old = self._checked(prior)
                    if old["event"] != event:
                        raise WatchError("Previously verified transfer changed; checkpoint retained")
                    continue
                self.db.execute("INSERT INTO events VALUES(?,?,?,?)",
                                (event["event_id"], canonical(packet), digest(packet), int(time.time())))
                if int(event["amount_units"]) >= minimum:
                    self.db.execute("INSERT INTO outbox(event_id) VALUES(?)", (event["event_id"],))
                added += 1
            if checkpoint is not None:
                self.db.execute("UPDATE state SET cursor_number=?,cursor_hash=? WHERE id=1", checkpoint)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
        return added

    @staticmethod
    def _checked(row: sqlite3.Row) -> dict[str, Any]:
        packet = json.loads(row["packet"])
        if digest(packet) != row["sha256"]:
            raise WatchError("Stored evidence digest mismatch")
        if verify_evidence(packet["evidence"], packet["event"]["watched_address"]) != packet["event"]:
            raise WatchError("Stored event does not reproduce from evidence")
        return packet

    def records(self) -> list[dict[str, Any]]:
        rows = self.db.execute("SELECT e.*,o.emitted_at,o.event_id AS notification_id FROM events e "
                               "LEFT JOIN outbox o USING(event_id) ORDER BY e.rowid").fetchall()
        return [{**self._checked(row), "evidence_sha256": row["sha256"],
                 "notification": ("below_threshold" if row["notification_id"] is None else
                                  "console_emitted" if row["emitted_at"] is not None else "pending")}
                for row in rows]

    def emit_pending(self, emit: Callable[[dict[str, Any]], None]) -> int:
        rows = self.db.execute("SELECT e.* FROM outbox o JOIN events e USING(event_id) "
                               "WHERE o.emitted_at IS NULL ORDER BY e.rowid").fetchall()
        for row in rows:
            packet = self._checked(row)
            emit({"type": "transfer_notification", "origin": packet["origin"],
                  **packet["event"], "evidence_sha256": row["sha256"]})
            # The sink must finish successfully before acknowledgment. A crash
            # between output and commit can repeat the same stable event_id.
            with self.db:
                self.db.execute("UPDATE outbox SET emitted_at=? WHERE event_id=?",
                                (int(time.time()), row["event_id"]))
        return len(rows)


class Monitor:
    def __init__(self, rpc: Any, history: History, address: str, *, minimum_units: int = 1_000_000) -> None:
        if type(minimum_units) is not int or not 0 <= minimum_units < 2**256:
            raise WatchError("Invalid minimum amount")
        self.rpc, self.history = rpc, history
        self.address = hex_data(address, 20)
        self.minimum = minimum_units
        history.bind(self.address, rpc.origin, self.minimum)

    def head(self) -> dict[str, Any]:
        if quantity(self.rpc.call("eth_chainId", [])) != 1:
            raise WatchError("Ethereum mainnet (chain ID 1) is required")
        return _block(self.rpc.call("eth_getBlockByNumber", ["finalized", False]))

    def packet(self, log: dict[str, Any], finalized: dict[str, Any]) -> dict[str, Any]:
        candidate = decode_log(log)
        evidence = {"chain_id": "0x1", "log": log,
                    "receipt": self.rpc.call("eth_getTransactionReceipt", [candidate["tx_hash"]]),
                    "block": self.rpc.call("eth_getBlockByNumber", [hex(candidate["block_number"]), False]),
                    "finalized": finalized}
        event = verify_evidence(evidence, self.address)
        return {"schema": "wallet-watch/0.1", "origin": self.rpc.origin, "source": self.rpc.source,
                "observed_at": int(time.time()), "event": event, "evidence": evidence}

    def _check_head(self, finalized: dict[str, Any]) -> None:
        current = _block(self.rpc.call("eth_getBlockByNumber", [finalized["number"], False]))
        if current["number"] != finalized["number"] or current["hash"].lower() != finalized["hash"].lower():
            raise WatchError("Finalized view changed during verification; checkpoint retained")

    def transaction(self, tx_hash: str) -> int:
        tx_hash = hex_data(tx_hash, 32)
        head = self.head()
        receipt = self.rpc.call("eth_getTransactionReceipt", [tx_hash])
        if not isinstance(receipt, dict) or not isinstance(receipt.get("logs"), list):
            raise WatchError("Transaction receipt unavailable")
        if hex_data(receipt.get("transactionHash"), 32) != tx_hash:
            raise WatchError("RPC returned a different transaction")
        packets = []
        for log in receipt["logs"]:
            if not isinstance(log, dict):
                raise WatchError("Malformed receipt log")
            if str(log.get("address", "")).lower() != USDC:
                continue
            topics = log.get("topics", [])
            if not isinstance(topics, list) or not topics or str(topics[0]).lower() != TRANSFER:
                continue
            candidate = decode_log(log)
            if candidate["tx_hash"] != tx_hash:
                raise WatchError("Receipt log belongs to a different transaction")
            if self.address in (candidate["from_address"], candidate["to_address"]):
                packets.append(self.packet(log, head))
        if not packets:
            raise WatchError("No USDC Transfer involving this address in the transaction")
        self._check_head(head)
        return self.history.save(packets, minimum=self.minimum)

    def scan(self, *, start_block: int | None = None, batch_size: int = 50) -> dict[str, Any]:
        if type(batch_size) is not int or not 1 <= batch_size <= 100:
            raise WatchError("Batch size must be 1..100 blocks")
        if start_block is not None and (type(start_block) is not int or start_block < 0):
            raise WatchError("Invalid starting block")
        head = self.head()
        finalized_number = quantity(head["number"])
        checkpoint = self.history.checkpoint()
        if checkpoint:
            if start_block is not None:
                raise WatchError("Existing checkpoint: omit --start-block when resuming")
            previous = _block(self.rpc.call("eth_getBlockByNumber", [hex(checkpoint[0]), False]))
            if (quantity(previous["number"]) != checkpoint[0]
                    or previous["hash"].lower() != checkpoint[1] or finalized_number < checkpoint[0]):
                raise WatchError("Finalized checkpoint changed or provider is behind; manual review required")
            start = checkpoint[0] + 1
        else:
            start = start_block if start_block is not None else max(0, finalized_number - batch_size + 1)
        end = min(finalized_number, start + batch_size - 1)
        if start > end:
            return {"status": "caught_up", "new_events": 0, "finalized_block": finalized_number}
        boundary = _block(self.rpc.call("eth_getBlockByNumber", [hex(end), False]))
        address_topic = "0x" + "0" * 24 + self.address[2:]
        logs: dict[tuple[str, int], dict[str, Any]] = {}
        for topics in ([TRANSFER, address_topic], [TRANSFER, None, address_topic]):
            result = self.rpc.call("eth_getLogs", [{"address": USDC, "fromBlock": hex(start),
                                   "toBlock": hex(end), "topics": topics}])
            if not isinstance(result, list) or len(result) > 2000:
                raise WatchError("Missing or oversized transfer result; reduce batch size")
            for log in result:
                candidate = decode_log(log)
                if not start <= candidate["block_number"] <= end:
                    raise WatchError("RPC returned a transfer outside the requested range")
                key = (candidate["tx_hash"], candidate["log_index"])
                if key in logs and decode_log(logs[key]) != candidate:
                    raise WatchError("Conflicting duplicate transfer logs")
                logs[key] = log
        packets = [self.packet(log, head) for log in sorted(logs.values(),
                   key=lambda item: (quantity(item["blockNumber"]), quantity(item["logIndex"])))]
        after = _block(self.rpc.call("eth_getBlockByNumber", [hex(end), False]))
        if after["number"] != hex(end) or boundary["number"] != hex(end) or after["hash"].lower() != boundary["hash"].lower():
            raise WatchError("Scan boundary changed; checkpoint retained")
        self._check_head(head)
        added = self.history.save(packets, minimum=self.minimum,
                    checkpoint=(end, boundary["hash"].lower()), expected=checkpoint)
        return {"status": "scanned", "from_block": start, "through_block": end,
                "finalized_block": finalized_number, "new_events": added,
                "coverage": "RPC returned logs for this range; provider completeness is not independently proven"}
