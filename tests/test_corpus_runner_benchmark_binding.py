from __future__ import annotations

import pytest

import resonance_arbitrage_graph.corpus_runner as corpus_runner
from resonance_arbitrage_graph.corpus_runner import CorpusRunnerConfig, build_research_report


class _FakeBundle:
    sha256 = "a" * 64


class _FakeCorpus:
    sha256 = "b" * 64

    def to_replay_bundle(self):
        return _FakeBundle()


def test_benchmark_payload_must_match_supplied_comparison_sha(monkeypatch):
    monkeypatch.setattr(corpus_runner, "terminal_operation_count", lambda _corpus: 3)
    config = CorpusRunnerConfig(
        min_terminal_operations=3,
        min_training_rows=2,
        benchmark_when_ready=True,
    )

    def bad_benchmark(_bundle, _min_training_rows):
        return {"paper_only": True, "value": 1}, "0" * 64

    with pytest.raises(ValueError, match="does not match payload"):
        build_research_report(
            _FakeCorpus(),
            config=config,
            benchmark_fn=bad_benchmark,
        )
