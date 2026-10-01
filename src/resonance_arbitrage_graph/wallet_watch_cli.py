"""Address -> verified USDC transfer -> console notification -> SQLite history."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sqlite3
import sys
import time

from .wallet_watch import DEFAULT_RPC, History, Monitor, Rpc, WatchError, canonical, usdc_units


def output(value: dict) -> None:
    print(json.dumps(value, ensure_ascii=False, sort_keys=True), flush=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("demo", "scan", "watch", "transaction", "history", "notifications"):
        command = commands.add_parser(name)
        command.add_argument("--db", type=Path, default=Path("wallet-data/watch.sqlite3"))
        if name in ("demo", "history", "notifications"):
            continue
        command.add_argument("--address", required=True, help="Public Ethereum address; no ownership is assumed")
        command.add_argument("--min-usdc", default="1", help="Notification threshold, up to six decimal places")
        command.add_argument("--rpc-url", default=None, help="Prefer WALLET_RPC_URL for URLs containing credentials")
        if name == "transaction":
            command.add_argument("--tx", required=True)
        else:
            command.add_argument("--start-block", type=int, help="First run only; otherwise resume saved checkpoint")
            command.add_argument("--batch-size", type=int, default=50)
            if name == "watch":
                command.add_argument("--poll-seconds", type=int, default=60)
    args = parser.parse_args(argv)
    history = None
    try:
        if args.command == "demo":
            from .wallet_watch_demo import run_demo
            return run_demo(args.db, output)
        if args.command in ("history", "notifications") and not args.db.is_file():
            raise WatchError("History does not exist; run a scan or verify a transaction first")
        if args.command == "watch" and args.poll_seconds < 15:
            raise WatchError("Polling interval must be at least 15 seconds")
        history = History(args.db)
        if args.command == "history":
            for row in history.records():
                output(row)
            return 0
        if args.command == "notifications":
            history.emit_pending(output)
            return 0
        rpc = Rpc(args.rpc_url or os.environ.get("WALLET_RPC_URL") or DEFAULT_RPC)
        monitor = Monitor(rpc, history, args.address, minimum_units=usdc_units(args.min_usdc))
        # Recover committed notifications even if this run's RPC is unavailable.
        history.emit_pending(output)
        if args.command == "transaction":
            result = {"status": "transaction_verified", "new_events": monitor.transaction(args.tx)}
            result["console_notifications"] = history.emit_pending(output)
            output(result)
            return 0
        start = args.start_block
        while True:
            result = monitor.scan(start_block=start, batch_size=args.batch_size)
            result["console_notifications"] = history.emit_pending(output)
            output(result)
            if args.command == "scan":
                return 0
            if history.checkpoint() is not None:
                start = None
            time.sleep(args.poll_seconds)
    except (WatchError, sqlite3.Error, OSError, KeyError, TypeError, json.JSONDecodeError) as exc:
        # RPC transport details and endpoint credentials are redacted in Rpc.
        message = str(exc) if isinstance(exc, WatchError) else "Local storage/output or evidence error"
        print(canonical({"status": "error", "message": message}), file=sys.stderr, flush=True)
        return 2
    except KeyboardInterrupt:
        return 130
    finally:
        if history is not None:
            history.close()


if __name__ == "__main__":
    raise SystemExit(main())
