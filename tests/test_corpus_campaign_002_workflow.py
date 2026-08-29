from pathlib import Path


WORKFLOW = Path(".github/workflows/corpus-campaign-002.yml")


def test_campaign_002_is_measurement_corrected_and_corpus_isolated():
    workflow = WORKFLOW.read_text(encoding="utf-8")

    assert "data/corpus-campaign-002" in workflow
    assert "campaign/002" in workflow
    assert "--campaign-id corpus-campaign-002" in workflow
    assert "--amount 25" in workflow
    assert "--max-cases 2" in workflow
    assert "--rolling-samples 6" in workflow
    assert "--rolling-horizon-ms 10000" in workflow
    assert "--rolling-min-coverage-ratio 0.5" in workflow
    assert "--max-quote-age-ms 3000" in workflow
    assert "--fee-bps 10" in workflow
    assert "--slippage-bps 2" in workflow
    assert "capacity-stress" not in workflow
    assert "campaign/001/corpus.json" not in workflow


def test_campaign_002_keeps_profile_failures_isolated_and_fail_closed():
    workflow = WORKFLOW.read_text(encoding="utf-8")

    command = "set +e\n            resonance-corpus-campaign-step"
    capture = "local code=$?\n            set -e"

    assert command in workflow
    assert capture in workflow
    assert workflow.index(command) < workflow.index(capture)
    assert "Fail closed on zero progress" in workflow


def test_campaign_001_is_frozen_after_measurement_contract_change():
    assert not Path(".github/workflows/corpus-campaign-001.yml").exists()
