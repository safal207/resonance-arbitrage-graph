"""Opt-in, read-only Binance client-path probe; never a trading/venue SLA benchmark."""
from __future__ import annotations

import argparse
from collections import Counter
from collections.abc import Callable
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import socket
import statistics
import sys
import time
import tracemalloc
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

from .adapters.binance import BinanceBookTickerAdapter
from .staleness import StalenessPolicy, assess_quote_staleness

PUBLIC_HOST = "data-api.binance.vision"
PATHS = {"/api/v3/exchangeInfo", "/api/v3/ticker/bookTicker"}
INSTRUMENTATION_ENV = (
    "PYTHONTRACEMALLOC", "PYTHONMALLOC", "PYTHONPROFILEIMPORTTIME",
    "PYTHONHASHSEED", "PYTHONASYNCIODEBUG", "COVERAGE_PROCESS_START",
)
PROXY_ENV = ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "NO_PROXY")


class NoRedirect(HTTPRedirectHandler):
    """Do not let a public-data request follow an unmeasured redirect."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def error_code(exc: Exception) -> str:
    reason = exc.reason if isinstance(exc, URLError) else exc
    if isinstance(exc, HTTPError):
        return "HTTP_ERROR"
    if isinstance(reason, TimeoutError):
        return "TIMEOUT"
    if isinstance(reason, socket.gaierror):
        return "DNS_ERROR"
    if isinstance(reason, OSError):
        return "NETWORK_ERROR"
    if isinstance(exc, (UnicodeDecodeError, json.JSONDecodeError)):
        return "DECODE_ERROR"
    if isinstance(exc, (ValueError, KeyError, TypeError)):
        return "INVALID_DATA"
    return "UNEXPECTED_ERROR"


def _object_json(body: bytes) -> dict[str, Any]:
    def reject_constant(value: str) -> None:
        raise ValueError("non-finite JSON number")
    payload = json.loads(body.decode("utf-8"), parse_constant=reject_constant)
    if not isinstance(payload, dict):
        raise ValueError("expected a JSON object")
    return payload


def _wall_now_ms() -> int:
    return time.time_ns() // 1_000_000


def _assessment_dict(assessment: Any) -> dict[str, Any]:
    data = asdict(assessment)
    data["verdict"] = assessment.verdict.value
    return data


class MeasuredJSON:
    """Single-threaded fetch_json callable, with no credentials or automatic retry.

    Instrumentation is opt-in. request_elapsed_ns stops before evidence recording;
    adapter_other_ns deliberately includes instrumentation bookkeeping overhead.
    A timeout is urllib's socket timeout, NOT a guaranteed whole-operation deadline.
    """

    def __init__(self, *, timeout: float = 5.0, max_bytes: int = 1_048_576,
                 opener: Any = None, clock: Callable[[], int] = time.perf_counter_ns,
                 wall_clock: Callable[[], int] = time.time_ns) -> None:
        if isinstance(timeout, bool) or not math.isfinite(timeout) or timeout <= 0:
            raise ValueError("timeout must be finite and positive")
        if type(max_bytes) is not int or max_bytes <= 0:
            raise ValueError("max_bytes must be a positive integer")
        self.timeout, self.max_bytes = timeout, max_bytes
        self.opener = opener if opener is not None else build_opener(NoRedirect())
        self.clock, self.wall_clock = clock, wall_clock
        self.attempt_count = 0
        self.requests: list[dict[str, Any]] = []
        self.bodies: dict[str, bytes] = {}

    @staticmethod
    def validate_url(url: str) -> str:
        parsed = urlsplit(url)
        query = parse_qs(parsed.query, keep_blank_values=True, strict_parsing=True)
        symbols = query.get("symbol", [])
        if (parsed.scheme != "https" or parsed.netloc != PUBLIC_HOST
                or parsed.path not in PATHS or parsed.fragment
                or set(query) != {"symbol"} or len(symbols) != 1
                or not symbols[0].isascii() or not symbols[0].isalnum()
                or symbols[0] != symbols[0].upper()):
            raise ValueError("only single-symbol public market-data HTTPS GETs are allowed")
        return parsed.path

    def __call__(self, url: str) -> dict[str, Any]:
        endpoint = self.validate_url(url)  # Rejected URLs never reach the network.
        request = Request(url, method="GET", headers={
            "Accept": "application/json", "User-Agent": "resonance-latency-probe/0.1",
        })
        row: dict[str, Any] = {
            "id": len(self.requests) + 1, "url": url, "endpoint": endpoint,
            "client_wall_start_ns": self.wall_clock(), "status": "ERROR",
            "http_status": None, "error_code": None, "error_type": None,
            "failed_stage": None, "open_to_headers_ns": None, "body_read_ns": None,
            "transport_to_body_ns": None, "decode_json_ns": None,
            "body_sha256": None, "body_bytes": None, "declared_body_bytes": None,
        }
        start = self.clock()
        stage = "open"
        body: bytes | None = None
        decode_start: int | None = None
        try:
            with self.opener.open(request, timeout=self.timeout) as response:
                headers_at = self.clock()
                row["open_to_headers_ns"] = headers_at - start
                row["http_status"] = response.status
                stage = "headers"
                if response.status != 200:
                    raise HTTPError(url, response.status, "non-200 response", {}, None)
                headers = getattr(response, "headers", {})
                declared = headers.get("Content-Length")
                if declared is not None:
                    if not declared.isascii() or not declared.isdecimal():
                        raise ValueError("invalid Content-Length")
                    row["declared_body_bytes"] = int(declared)
                    if int(declared) > self.max_bytes:
                        raise ValueError("declared response body exceeds limit")
                stage = "read"
                read_start = self.clock()
                body = response.read(self.max_bytes + 1)
                body_at = self.clock()
                row["body_read_ns"] = body_at - read_start
                row["transport_to_body_ns"] = body_at - start
                if len(body) > self.max_bytes:
                    raise ValueError("response body exceeds limit")
                if declared is not None and len(body) != int(declared):
                    raise ValueError("incomplete response body")
            stage = "decode"
            decode_start = self.clock()
            payload = _object_json(body)
            row["decode_json_ns"] = self.clock() - decode_start
            row["status"] = "OK"
            return payload
        except Exception as exc:
            row.update(error_code=error_code(exc), error_type=type(exc).__name__, failed_stage=stage)
            if isinstance(exc, HTTPError):
                row["http_status"] = exc.code
                exc.close()
            raise
        finally:
            end = self.clock()
            row["request_elapsed_ns"] = end - start
            if decode_start is not None and row["decode_json_ns"] is None:
                row["decode_json_ns"] = end - decode_start
            # No response strings, proxy credentials, or environment values in errors.
            if body is not None:
                digest = hashlib.sha256(body).hexdigest()
                row.update(body_sha256=digest, body_bytes=len(body))
                self.bodies[digest] = body
            self.requests.append(row)


def probe(adapter: BinanceBookTickerAdapter, fetcher: MeasuredJSON, *,
          samples: int = 3, interval: float = 0.0,
          sleeper: Callable[[float], None] = time.sleep,
          staleness_policy: StalenessPolicy | None = None,
          staleness_now_ms: Callable[[], int] = _wall_now_ms) -> list[dict[str, Any]]:
    """Probe one fixed pair; keep failures and never retry/reroute failed requests.

    Staleness assessment, when requested, runs after the adapter timing interval is
    closed so policy evaluation is not attributed to ``adapter_total_ns``.
    """
    if type(samples) is not int or not 1 <= samples <= 1001:
        raise ValueError("samples must be an integer in 1..1001")
    if isinstance(interval, bool) or not math.isfinite(interval) or interval < 0:
        raise ValueError("interval must be finite and non-negative")
    results = []
    for index in range(samples):
        before = len(fetcher.requests)
        started = fetcher.clock()
        fetcher.attempt_count += 1
        row: dict[str, Any] = {"id": fetcher.attempt_count, "status": "ERROR", "error_code": None,
                               "error_type": None, "snapshot": None, "staleness": None,
                               "verifier_ns": None, "source_age_ms": None}
        try:
            snapshot = adapter.fetch("BTCUSDT", base_asset="BTC", quote_asset="USDT")
        except Exception as exc:
            row.update(error_code=error_code(exc), error_type=type(exc).__name__)
        else:
            row["status"] = "OK"
            # Defer serialization and staleness evaluation until adapter timing is closed.
        ended = fetcher.clock()
        if row["status"] == "OK":
            row["snapshot"] = asdict(snapshot)
            if staleness_policy is not None:
                assessment = assess_quote_staleness(
                    snapshot, now_ms=staleness_now_ms(), policy=staleness_policy,
                )
                row["staleness"] = _assessment_dict(assessment)
                # Backward-compatible top-level alias; remains None when source age is unavailable.
                row["source_age_ms"] = assessment.source_age_ms
        requests = fetcher.requests[before:]
        metadata_requested = any(r["endpoint"].endswith("exchangeInfo") for r in requests)
        row["metadata_regime"] = (
            "metadata_requested" if metadata_requested else
            "metadata_cache_reused" if requests else "no_request"
        )
        for request_row in requests:
            request_row["metadata_regime"] = row["metadata_regime"]
            request_row["adapter_attempt_id"] = row["id"]
        row["request_ids"] = [r["id"] for r in requests]
        row["adapter_total_ns"] = ended - started
        row["adapter_other_ns"] = row["adapter_total_ns"] - sum(r["request_elapsed_ns"] for r in requests)
        if row["adapter_other_ns"] < 0:
            raise RuntimeError("inconsistent monotonic intervals")
        results.append(row)
        if row["status"] != "OK":
            break  # Preserve evidence and stop, including on HTTP 418/429.
        if index + 1 < samples and interval:
            sleeper(interval)  # Outside the measured adapter interval.
    return results


def distribution(values: list[int]) -> dict[str, Any]:
    """Empirical nearest-rank tails, suppressed below an explicit sample policy.

    Minimum counts do not establish confidence or remove serial correlation.
    """
    if any(type(v) is not int or v < 0 for v in values):
        raise ValueError("durations must be non-negative integers")
    ordered = sorted(values)
    n = len(ordered)
    return {"n": n, "median_ns": statistics.median(ordered) if n else None,
            "max_ns": ordered[-1] if n else None,
            "p95_ns": ordered[math.ceil(.95 * n) - 1] if n >= 100 else None,
            "p99_ns": ordered[math.ceil(.99 * n) - 1] if n >= 1000 else None}


def summarize(attempts: list[dict[str, Any]], requests: list[dict[str, Any]]) -> dict[str, Any]:
    adapter_groups: dict[str, Any] = {}
    for regime in sorted({a["metadata_regime"] for a in attempts}):
        rows = [a for a in attempts if a["metadata_regime"] == regime]
        adapter_groups[regime] = {
            "attempts": len(rows), "errors": sum(a["status"] != "OK" for a in rows),
            "success_adapter_total_ns": distribution([a["adapter_total_ns"] for a in rows if a["status"] == "OK"]),
            "failed_adapter_elapsed_ns": distribution([a["adapter_total_ns"] for a in rows if a["status"] != "OK"]),
        }
    request_groups = {}
    keys = {(r["endpoint"], r.get("metadata_regime", "unassigned")) for r in requests}
    for endpoint, regime in sorted(keys):
        rows = [r for r in requests if r["endpoint"] == endpoint
                and r.get("metadata_regime", "unassigned") == regime]
        ok = [r for r in rows if r["status"] == "OK"]
        request_groups.setdefault(endpoint, {})[regime] = {
            "attempts": len(rows), "errors": sum(r["status"] != "OK" for r in rows),
            "success_transport_to_body_ns": distribution([r["transport_to_body_ns"] for r in ok]),
            "success_decode_json_ns": distribution([r["decode_json_ns"] for r in ok]),
            "failed_request_elapsed_ns": distribution([r["request_elapsed_ns"] for r in rows if r["status"] != "OK"]),
        }
    staleness_counts = Counter(
        a["staleness"]["verdict"] for a in attempts if a.get("staleness") is not None
    )
    return {"attempted_samples": len(attempts), "successful_samples": sum(a["status"] == "OK" for a in attempts),
            "errors_by_code": dict(Counter(a["error_code"] for a in attempts if a["status"] != "OK")),
            "staleness_by_verdict": dict(staleness_counts),
            "adapter_by_metadata_regime": adapter_groups, "requests_by_endpoint_and_metadata_regime": request_groups}


class FixtureOpener:
    """Synthetic data, optionally delayed; never an exchange latency measurement."""

    def __init__(self, delay_ms: float = 0.0) -> None:
        if not math.isfinite(delay_ms) or not 0 <= delay_ms <= 2000:
            raise ValueError("fixture delay must be in 0..2000 ms")
        self.delay_ms = delay_ms

    def open(self, request: Request, *, timeout: float):
        is_quote = request.full_url.split("?")[0].endswith("bookTicker")
        if is_quote and self.delay_ms:
            time.sleep(self.delay_ms / 1000)
        payload = ({"symbol": "BTCUSDT", "bidPrice": "60000", "bidQty": "1",
                    "askPrice": "60001", "askQty": "2"} if is_quote else {
                    "symbols": [{"symbol": "BTCUSDT", "status": "TRADING",
                                 "baseAsset": "BTC", "quoteAsset": "USDT", "isSpotTradingAllowed": True}]})
        class Response:
            status = 200
            def __enter__(self):
                return self
            def __exit__(self, *args):
                return False
            def read(self, size):
                return json.dumps(payload).encode()[:size]
        return Response()


def environment() -> dict[str, Any]:
    clock = time.get_clock_info("perf_counter")
    return {"python": platform.python_version(), "implementation": platform.python_implementation(),
            "platform": platform.platform(), "clock_implementation": clock.implementation,
            "clock_monotonic": clock.monotonic, "clock_resolution_seconds": clock.resolution,
            "trace_active": sys.gettrace() is not None, "profile_active": sys.getprofile() is not None,
            "tracemalloc_active": tracemalloc.is_tracing(),
            "instrumentation_env_names": [k for k in INSTRUMENTATION_ENV if k in os.environ],
            "proxy_env_names": [k for k in PROXY_ENV + tuple(k.lower() for k in PROXY_ENV) if k in os.environ],
            "environment_isolated": False}


def write_bundle(directory: Path, report: dict[str, Any], bodies: dict[str, bytes]) -> None:
    """Write into a fresh directory; hashes bind bytes, not origin or completeness."""
    directory.mkdir(parents=True, exist_ok=False)
    raw_dir = directory / "raw"
    raw_dir.mkdir()
    manifest = {}
    for digest, body in bodies.items():
        if hashlib.sha256(body).hexdigest() != digest:
            raise ValueError("raw body digest mismatch")
        (raw_dir / f"{digest}.bin").write_bytes(body)
        manifest[f"raw/{digest}.bin"] = digest
    content = (json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()
    (directory / "report.json").write_bytes(content)
    manifest["report.json"] = hashlib.sha256(content).hexdigest()
    (directory / "sha256.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true", help="Explicitly enable public HTTPS GETs")
    parser.add_argument("--samples", type=int, default=3)
    parser.add_argument("--interval", type=float, default=1.0, help="Seconds; live mode requires >=1")
    parser.add_argument("--timeout", type=float, default=5.0, help="Socket timeout, not end-to-end deadline")
    parser.add_argument("--fixture-delay-ms", type=float, default=0.0)
    parser.add_argument("--max-observation-age-ms", type=int, default=None,
                        help="Caller-supplied local observation-age bound; omitted means no staleness assessment")
    parser.add_argument("--max-source-age-ms", type=int, default=None,
                        help="Optional exchange-published snapshot-age bound; requires --max-observation-age-ms")
    parser.add_argument("--output", type=Path, required=True, help="New directory; never overwrite")
    args = parser.parse_args(argv)
    if args.output.exists():
        parser.error("output already exists; use a fresh directory")
    if (not 1 <= args.samples <= 1001 or not math.isfinite(args.interval) or args.interval < 0
            or not math.isfinite(args.timeout) or args.timeout <= 0
            or not math.isfinite(args.fixture_delay_ms) or not 0 <= args.fixture_delay_ms <= 2000):
        parser.error("invalid sample, interval, timeout, or fixture-delay value")
    if args.max_observation_age_ms is not None and args.max_observation_age_ms < 0:
        parser.error("max-observation-age-ms must be non-negative")
    if args.max_source_age_ms is not None:
        if args.max_source_age_ms < 0:
            parser.error("max-source-age-ms must be non-negative")
        if args.max_observation_age_ms is None:
            parser.error("max-source-age-ms requires max-observation-age-ms")
    if args.live and (args.interval < 1 or args.fixture_delay_ms != 0):
        parser.error("live mode requires interval >=1 and forbids fixture delay")
    staleness_policy = (
        StalenessPolicy(
            max_observation_age_ms=args.max_observation_age_ms,
            max_source_age_ms=args.max_source_age_ms,
        )
        if args.max_observation_age_ms is not None else None
    )
    fetcher = MeasuredJSON(timeout=args.timeout, opener=None if args.live else FixtureOpener(args.fixture_delay_ms))
    adapter = BinanceBookTickerAdapter(fetch_json=fetcher)
    # Both supported public endpoints use one host. Existing adapter defaults are unchanged.
    adapter.metadata_base_url = adapter.base_url
    attempts = probe(
        adapter, fetcher, samples=args.samples, interval=args.interval if args.live else 0,
        staleness_policy=staleness_policy,
    )
    report = {
        "schema": "resonance-client-latency/v2", "source_kind": "LIVE_PUBLIC_HTTP" if args.live else "SYNTHETIC_FIXTURE",
        "captured_at_utc": datetime.now(timezone.utc).isoformat(), "environment": environment(),
        "config": {"symbol": "BTCUSDT", "requested_samples": args.samples, "socket_timeout_seconds": args.timeout,
                   "interval_seconds": args.interval if args.live else 0, "fixture_delay_ms": args.fixture_delay_ms,
                   "retries": 0, "redirects": False, "max_body_bytes": fetcher.max_bytes,
                   "staleness_policy": asdict(staleness_policy) if staleness_policy is not None else None},
        "completed_requested_samples": len(attempts) == args.samples,
        "stop_reason": None if attempts[-1]["status"] == "OK" else attempts[-1]["error_code"],
        "claim_boundary": {
            "client_path_only": True, "exchange_source_timestamp_available": False,
            "pure_exchange_latency_measured": False, "trading_or_order_recovery_tested": False,
            "verifier_measured": False, "connection_reuse_asserted": False,
            "measurement_overhead_subtracted": False, "hashes_authenticate_exchange": False,
            "staleness_policy_applied": staleness_policy is not None,
            "source_age_claim_requires_exchange_published_timestamp": True,
        },
        "percentile_policy": {"method": "nearest_rank", "p95_min_successes": 100, "p99_min_successes": 1000,
                              "confidence_guarantee": False},
        "source_sha256": {
            name: hashlib.sha256((Path(__file__).parent / name).read_bytes()).hexdigest()
            for name in ("latency_probe.py", "staleness.py", "adapters/binance.py", "adapters/http.py",
                         "quotes.py", "model.py", "validation.py")
        },
        "attempts": attempts, "requests": fetcher.requests, "summary": summarize(attempts, fetcher.requests),
    }
    write_bundle(args.output, report, fetcher.bodies)
    print(json.dumps({"output": str(args.output), "source_kind": report["source_kind"],
                      "summary": report["summary"], "stop_reason": report["stop_reason"]}, indent=2))
    return 0 if all(a["status"] == "OK" for a in attempts) else 1


if __name__ == "__main__":
    raise SystemExit(main())
