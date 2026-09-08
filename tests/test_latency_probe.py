from __future__ import annotations

import hashlib
import json
from pathlib import Path
import socket
from urllib.error import HTTPError, URLError

import pytest

from resonance_arbitrage_graph.adapters.binance import BinanceBookTickerAdapter
from resonance_arbitrage_graph.latency_probe import (
    FixtureOpener, MeasuredJSON, NoRedirect, distribution, environment,
    main, probe, summarize, write_bundle,
)

HOST = "https://data-api.binance.vision"
QUOTE = HOST + "/api/v3/ticker/bookTicker?symbol=BTCUSDT"
METADATA = HOST + "/api/v3/exchangeInfo?symbol=BTCUSDT"


class Clock:
    def __init__(self):
        self.now = 0
    def __call__(self):
        return self.now
    def advance(self, n):
        self.now += n


class Opener:
    def __init__(self, clock, *, open_ns=11, read_ns=7, fault=None, body=None, status=200, headers=None):
        self.clock = clock
        self.open_ns, self.read_ns = open_ns, read_ns
        self.fault, self.body, self.status = fault, body, status
        self.headers = headers or {}
        self.calls = []
        self.closed = 0

    def open(self, request, *, timeout):
        self.calls.append(request)
        self.clock.advance(self.open_ns)
        if self.fault == "open":
            raise TimeoutError("not an exchange acknowledgement")
        if isinstance(self.fault, Exception):
            raise self.fault
        parent = self
        class Response:
            status = parent.status
            headers = parent.headers
            def __enter__(self):
                return self
            def __exit__(self, *args):
                parent.closed += 1
            def read(self, n):
                parent.clock.advance(parent.read_ns)
                if parent.fault == "read":
                    raise TimeoutError("partial read")
                if parent.body is not None:
                    return parent.body[:n]
                with FixtureOpener().open(request, timeout=timeout) as response:
                    return response.read(n)
        return Response()


def make(*, clock=None, **kwargs):
    clock = clock or Clock()
    opener = Opener(clock, **kwargs)
    fetcher = MeasuredJSON(opener=opener, clock=clock, wall_clock=lambda: 123)
    adapter = BinanceBookTickerAdapter(fetch_json=fetcher)
    adapter.metadata_base_url = adapter.base_url
    return adapter, fetcher, opener, clock


def test_exact_nonoverlapping_transport_phases_and_hash():
    adapter, fetcher, opener, _ = make()
    result = probe(adapter, fetcher, samples=1)
    assert result[0]["adapter_total_ns"] == 36
    for row in fetcher.requests:
        assert row["open_to_headers_ns"] == 11
        assert row["body_read_ns"] == 7
        assert row["transport_to_body_ns"] == 18
        assert row["request_elapsed_ns"] == 18
        assert row["decode_json_ns"] == 0  # Controlled clock: no elapsed decode time injected.
        assert hashlib.sha256(fetcher.bodies[row["body_sha256"]]).hexdigest() == row["body_sha256"]
    assert opener.closed == 2


def test_real_adapter_metadata_cache_is_not_connection_warmth():
    adapter, fetcher, _, _ = make()
    rows = probe(adapter, fetcher, samples=3)
    assert [r["metadata_regime"] for r in rows] == ["metadata_requested", "metadata_cache_reused", "metadata_cache_reused"]
    assert [len(r["request_ids"]) for r in rows] == [2, 1, 1]
    assert [r["adapter_total_ns"] for r in rows] == [36, 18, 18]
    summary = summarize(rows, fetcher.requests)
    by_quote = summary["requests_by_endpoint_and_metadata_regime"]["/api/v3/ticker/bookTicker"]
    assert by_quote["metadata_requested"]["attempts"] == 1
    assert by_quote["metadata_cache_reused"]["attempts"] == 2


def test_controlled_delay_adds_exact_delta_without_mutating_quote_semantics():
    a, f, o, _ = make()
    probe(a, f, samples=1)  # Populate metadata before BOTH compared attempts.
    baseline = probe(a, f, samples=1)[0]
    o.open_ns += 1_000_000
    delayed = probe(a, f, samples=1)[0]
    assert baseline["metadata_regime"] == delayed["metadata_regime"] == "metadata_cache_reused"
    assert delayed["adapter_total_ns"] - baseline["adapter_total_ns"] == 1_000_000
    assert delayed["id"] > baseline["id"]
    for key in ("symbol", "bid_price", "ask_price", "timestamp_class", "source_timestamp_ms"):
        assert baseline["snapshot"][key] == delayed["snapshot"][key]
    assert delayed["source_age_ms"] is None and delayed["verifier_ns"] is None


def test_wall_clock_jumps_do_not_change_monotonic_durations():
    a, f, _, _ = make()
    times = iter([10**18, 1])
    f.wall_clock = lambda: next(times)
    rows = probe(a, f, samples=1)
    assert rows[0]["adapter_total_ns"] == 36
    assert f.requests[0]["client_wall_start_ns"] > f.requests[1]["client_wall_start_ns"]


@pytest.mark.parametrize("stage", ["open", "read"])
def test_timeouts_record_failure_and_stop_without_retry(stage):
    a, f, o, _ = make(fault=stage)
    rows = probe(a, f, samples=3)
    assert len(rows) == len(o.calls) == 1
    assert rows[0]["status"] == "ERROR" and rows[0]["snapshot"] is None
    record = f.requests[0]
    assert record["error_code"] == "TIMEOUT" and record["failed_stage"] == stage
    assert record["transport_to_body_ns"] is None and record["decode_json_ns"] is None
    summary = summarize(rows, f.requests)
    stats = summary["adapter_by_metadata_regime"]["metadata_requested"]
    assert stats["success_adapter_total_ns"]["n"] == 0
    assert stats["failed_adapter_elapsed_ns"]["n"] == 1


def test_dns_failure_is_not_exchange_timeout():
    a, f, _, _ = make(fault=URLError(socket.gaierror(-2, "name not found")))
    row = probe(a, f, samples=3)[0]
    assert row["error_code"] == f.requests[0]["error_code"] == "DNS_ERROR"


@pytest.mark.parametrize("status", [302, 418, 429, 503])
def test_http_failure_retains_status_and_stops(status):
    a, f, o, _ = make(fault=HTTPError(METADATA, status, "response", {}, None))
    rows = probe(a, f, samples=3)
    assert len(rows) == len(o.calls) == 1
    assert f.requests[0]["http_status"] == status
    assert rows[0]["error_code"] == "HTTP_ERROR"


@pytest.mark.parametrize("body", [b"not JSON", b"\xff", b"[]", b"null", b'{"v": NaN}'])
def test_bad_json_preserves_raw_evidence_not_success(body):
    a, f, _, _ = make(body=body)
    rows = probe(a, f, samples=1)
    request = f.requests[0]
    assert rows[0]["status"] == request["status"] == "ERROR"
    assert request["failed_stage"] == "decode"
    assert f.bodies[request["body_sha256"]] == body


def test_payload_limit_closes_response_and_is_not_success():
    a, f, o, _ = make(body=b"x" * 100)
    f.max_bytes = 10
    rows = probe(a, f, samples=1)
    assert rows[0]["status"] == "ERROR" and o.closed == 1
    assert f.requests[0]["body_bytes"] == 11
    assert f.requests[0]["failed_stage"] == "read"


def test_adapter_rejection_is_distinct_from_http_json_success():
    a, f, _, _ = make(body=b'{"symbols": []}')
    rows = probe(a, f, samples=1)
    assert rows[0]["status"] == "ERROR"
    assert f.requests[0]["status"] == "OK"
    assert rows[0]["error_code"] == "INVALID_DATA"


@pytest.mark.parametrize("url", [
    "http://data-api.binance.vision/api/v3/exchangeInfo?symbol=BTCUSDT",
    "https://api.binance.com/api/v3/exchangeInfo?symbol=BTCUSDT",
    HOST + "/api/v3/order?symbol=BTCUSDT",
    QUOTE + "&signature=secret", QUOTE + "&symbol=ETHUSDT", QUOTE + "#fragment",
    "https://user:secret@data-api.binance.vision/api/v3/exchangeInfo?symbol=BTCUSDT",
    HOST + "/api/v3/exchangeInfo?symbol=", HOST + "/api/v3/exchangeInfo?symbol=btc",
])
def test_endpoint_restrictions_precede_network(url):
    _, f, o, _ = make()
    with pytest.raises(ValueError):
        f(url)
    assert not o.calls and not f.requests


def test_request_is_get_has_no_auth_and_redirects_are_disabled():
    a, f, o, _ = make()
    probe(a, f, samples=1)
    for request in o.calls:
        assert request.get_method() == "GET" and request.data is None
        assert not any("auth" in key.lower() or "api-key" in key.lower() for key, _ in request.header_items())
    assert NoRedirect().redirect_request(None, None, 302, "", {}, "https://elsewhere") is None


def test_percentiles_suppressed_by_sample_size_and_nearest_rank():
    assert distribution([])["median_ns"] is None
    assert distribution([5])["p95_ns"] is None
    assert distribution(list(range(99)))["p95_ns"] is None
    assert distribution(list(range(100)))["p95_ns"] == 94
    assert distribution(list(range(999)))["p99_ns"] is None
    assert distribution(list(range(1000)))["p99_ns"] == 989


@pytest.mark.parametrize("values", [[-1], [1.5], [True]])
def test_invalid_durations_rejected(values):
    with pytest.raises(ValueError):
        distribution(values)


def test_sleep_is_excluded_from_measurements():
    a, f, _, clock = make()
    rows = probe(a, f, samples=2, interval=10, sleeper=lambda _: clock.advance(10**10))
    assert [r["adapter_total_ns"] for r in rows] == [36, 18]


def test_default_cli_offline_bundle_and_hashes(tmp_path, capsys):
    out = tmp_path / "fixture"
    assert main(["--output", str(out)]) == 0
    report = json.loads((out / "report.json").read_text())
    assert report["source_kind"] == "SYNTHETIC_FIXTURE"
    assert report["summary"]["successful_samples"] == 3
    assert report["claim_boundary"]["verifier_measured"] is False
    assert report["source_sha256"]["adapters/binance.py"]
    for name, digest in json.loads((out / "sha256.json").read_text()).items():
        assert hashlib.sha256((out / name).read_bytes()).hexdigest() == digest
    with pytest.raises(SystemExit):
        main(["--output", str(out)])


def test_bundle_never_overwrites_and_rejects_bad_raw_hash(tmp_path):
    with pytest.raises(ValueError):
        write_bundle(tmp_path / "bad", {}, {"0" * 64: b"different"})
    with pytest.raises(FileExistsError):
        write_bundle(tmp_path, {}, {})


def test_environment_records_presence_without_secrets(monkeypatch):
    monkeypatch.setenv("HTTPS_PROXY", "https://user:secret@proxy.example")
    monkeypatch.setenv("PYTHONTRACEMALLOC", "secret-value")
    data = environment()
    serialized = json.dumps(data)
    assert "HTTPS_PROXY" in data["proxy_env_names"]
    assert "PYTHONTRACEMALLOC" in data["instrumentation_env_names"]
    assert "secret" not in serialized and "proxy.example" not in serialized


@pytest.mark.parametrize("args", [["--samples", "0"], ["--samples", "1002"],
                                  ["--interval", "nan"], ["--timeout", "inf"],
                                  ["--live", "--interval", "0"],
                                  ["--live", "--fixture-delay-ms", "1"]])
def test_invalid_cli_inputs_rejected_before_network(tmp_path, args):
    with pytest.raises(SystemExit):
        main(["--output", str(tmp_path / "new"), *args])
    assert not (tmp_path / "new").exists()


def test_bad_quote_does_not_bypass_existing_snapshot_validation():
    a, f, o, _ = make()
    probe(a, f, samples=1)  # Valid metadata now cached.
    o.body = b'{"symbol":"BTCUSDT","bidPrice":"NaN","bidQty":"1","askPrice":"60001","askQty":"1"}'
    rows = probe(a, f, samples=2)
    assert len(rows) == 1 and rows[0]["status"] == "ERROR"
    assert rows[0]["metadata_regime"] == "metadata_cache_reused"
    assert f.requests[-1]["status"] == "OK"  # HTTP + JSON OK; adapter rejected data.
    assert rows[0]["snapshot"] is None


def test_failed_metadata_request_does_not_mark_next_run_as_warm():
    a, f, o, _ = make(fault="open")
    probe(a, f, samples=1)
    o.fault = None
    rows = probe(a, f, samples=1)
    assert rows[0]["metadata_regime"] == "metadata_requested"
    assert len(rows[0]["request_ids"]) == 2


@pytest.mark.parametrize("declared", ["100", "-1", "bad", "10000000000"])
def test_truncated_or_bad_declared_length_cannot_count_as_success(declared):
    a, f, o, _ = make(body=b'{"symbols":[]}', headers={"Content-Length": declared})
    rows = probe(a, f, samples=1)
    assert rows[0]["status"] == f.requests[0]["status"] == "ERROR"
    assert o.closed == 1


def test_valid_content_length_retains_declared_size():
    _, f, _, _ = make(body=b'{"ok":1}', headers={"Content-Length": "8"})
    assert f(QUOTE) == {"ok": 1}
    assert f.requests[0]["declared_body_bytes"] == 8


def test_header_processing_is_not_attributed_to_body_read():
    clock = Clock()
    class SlowHeader(str):
        def isascii(self):
            clock.advance(101)
            return True
    _, f, _, _ = make(clock=clock, body=b'{"ok":1}', headers={"Content-Length": SlowHeader("8")})
    assert f(QUOTE) == {"ok": 1}
    row = f.requests[0]
    assert row["open_to_headers_ns"] == 11
    assert row["body_read_ns"] == 7
    assert row["transport_to_body_ns"] == 11 + 101 + 7
