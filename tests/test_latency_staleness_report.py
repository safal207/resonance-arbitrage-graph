from __future__ import annotations

import json

import pytest

from resonance_arbitrage_graph.adapters.binance import BinanceBookTickerAdapter
from resonance_arbitrage_graph.latency_probe import FixtureOpener, MeasuredJSON, main, probe
from resonance_arbitrage_graph.staleness import StalenessPolicy


def _adapter() -> tuple[BinanceBookTickerAdapter, MeasuredJSON]:
    fetcher = MeasuredJSON(opener=FixtureOpener())
    adapter = BinanceBookTickerAdapter(fetch_json=fetcher)
    adapter.metadata_base_url = adapter.base_url
    return adapter, fetcher


def test_probe_attaches_fresh_observation_only_assessment(monkeypatch) -> None:
    monkeypatch.setattr(
        "resonance_arbitrage_graph.adapters.binance.time.time_ns",
        lambda: 1_000_000_000,
    )
    adapter, fetcher = _adapter()
    rows = probe(
        adapter,
        fetcher,
        samples=1,
        staleness_policy=StalenessPolicy(max_observation_age_ms=5),
        staleness_now_ms=lambda: 1_004,
    )
    assessment = rows[0]["staleness"]
    assert assessment["verdict"] == "FRESH"
    assert assessment["observation_age_ms"] == 4
    assert assessment["source_age_ms"] is None
    assert rows[0]["source_age_ms"] is None


def test_binance_source_age_requirement_is_unknown_not_fresh(monkeypatch) -> None:
    monkeypatch.setattr(
        "resonance_arbitrage_graph.adapters.binance.time.time_ns",
        lambda: 1_000_000_000,
    )
    adapter, fetcher = _adapter()
    rows = probe(
        adapter,
        fetcher,
        samples=1,
        staleness_policy=StalenessPolicy(
            max_observation_age_ms=5,
            max_source_age_ms=5,
        ),
        staleness_now_ms=lambda: 1_004,
    )
    assessment = rows[0]["staleness"]
    assert assessment["verdict"] == "UNKNOWN"
    assert "SOURCE_PUBLICATION_TIMESTAMP_UNAVAILABLE" in assessment["reasons"]


def test_cli_report_wires_policy_and_unknown_verdict(tmp_path) -> None:
    out = tmp_path / "evidence"
    assert main([
        "--max-observation-age-ms", "60000",
        "--max-source-age-ms", "60000",
        "--output", str(out),
    ]) == 0
    report = json.loads((out / "report.json").read_text())
    assert report["schema"] == "resonance-client-latency/v2"
    assert report["config"]["staleness_policy"] == {
        "max_observation_age_ms": 60000,
        "max_source_age_ms": 60000,
    }
    assert report["claim_boundary"]["staleness_policy_applied"] is True
    assert report["summary"]["staleness_by_verdict"] == {"UNKNOWN": 3}
    assert all(row["staleness"]["verdict"] == "UNKNOWN" for row in report["attempts"])


def test_cli_without_policy_keeps_assessment_opt_in(tmp_path) -> None:
    out = tmp_path / "evidence"
    assert main(["--output", str(out)]) == 0
    report = json.loads((out / "report.json").read_text())
    assert report["config"]["staleness_policy"] is None
    assert report["claim_boundary"]["staleness_policy_applied"] is False
    assert report["summary"]["staleness_by_verdict"] == {}
    assert all(row["staleness"] is None for row in report["attempts"])


@pytest.mark.parametrize("args", [
    ["--max-observation-age-ms", "-1"],
    ["--max-source-age-ms", "10"],
    ["--max-observation-age-ms", "10", "--max-source-age-ms", "-1"],
])
def test_invalid_staleness_cli_policy_is_rejected_before_output(tmp_path, args) -> None:
    out = tmp_path / "evidence"
    with pytest.raises(SystemExit):
        main([*args, "--output", str(out)])
    assert not out.exists()
