"""Explicitly synthetic, offline demonstration of the complete wallet pipeline."""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any, Callable

from .wallet_watch import History, Monitor, TRANSFER, USDC, WatchError

DEMO_ADDRESS = "0x" + "22" * 20
DEMO_TX = "0x" + "44" * 32


def fixture() -> dict[str, Any]:
    block = {"number": "0x64", "hash": "0x" + "aa" * 32, "timestamp": "0x6553f100"}
    head = {"number": "0x6e", "hash": "0x" + "bb" * 32, "timestamp": "0x6553f178"}
    log = {"address": USDC, "topics": [TRANSFER, "0x" + "0" * 24 + "11" * 20,
           "0x" + "0" * 24 + "22" * 20], "data": "0x" + f"{125_500_000:064x}",
           "transactionHash": DEMO_TX, "logIndex": "0x3", "blockNumber": block["number"],
           "blockHash": block["hash"], "removed": False}
    receipt = {"transactionHash": DEMO_TX, "blockNumber": block["number"],
               "blockHash": block["hash"], "status": "0x1", "logs": [deepcopy(log)]}
    return {"block": block, "finalized": head, "log": log, "receipt": receipt}


class FixtureRpc:
    origin = "SYNTHETIC_FIXTURE"
    source = "offline-demo"

    def __init__(self) -> None:
        self.data = fixture()
        self.calls: list[tuple[str, list[Any]]] = []

    def call(self, method: str, params: list[Any]) -> Any:
        self.calls.append((method, deepcopy(params)))
        if method == "eth_chainId":
            return "0x1"
        if method == "eth_getBlockByNumber":
            if params[0] in ("finalized", self.data["finalized"]["number"]):
                return deepcopy(self.data["finalized"])
            if params[0] == self.data["block"]["number"]:
                return deepcopy(self.data["block"])
            raise WatchError("No block in the synthetic fixture")
        if method == "eth_getTransactionReceipt":
            return deepcopy(self.data["receipt"]) if params[0] == DEMO_TX else None
        if method == "eth_getLogs":
            query = params[0]
            log = self.data["log"]
            if not int(query["fromBlock"], 16) <= int(log["blockNumber"], 16) <= int(query["toBlock"], 16):
                return []
            if all(wanted is None or wanted == actual for wanted, actual in zip(query["topics"], log["topics"])):
                return [deepcopy(log)]
            return []
        raise WatchError("Unsupported offline fixture request")


def run_demo(path: Path, emit: Callable[[dict[str, Any]], None]) -> int:
    history = History(path)
    try:
        monitor = Monitor(FixtureRpc(), history, DEMO_ADDRESS)
        result = monitor.scan()
        emitted = history.emit_pending(emit)
        before = len(history.records())
    finally:
        history.close()
    restarted = History(path)
    try:
        duplicate = Monitor(FixtureRpc(), restarted, DEMO_ADDRESS).transaction(DEMO_TX)
        replay_notifications = restarted.emit_pending(emit)
        records = restarted.records()
        if len(records) != before or duplicate != 0 or replay_notifications != 0:
            raise WatchError("Demo restart/deduplication check failed")
        emit({"type": "demo_result", "origin": "SYNTHETIC_FIXTURE", "scan": result,
              "new_console_notifications": emitted, "history_events": len(records),
              "restart_new_events": duplicate, "restart_notifications": replay_notifications,
              "database": str(path), "live_rpc_verified": False,
              "note": "Synthetic transfer; does not assert any real wallet activity"})
    finally:
        restarted.close()
    return 0
