from pathlib import Path


WORKFLOW = Path(".github/workflows/corpus-campaign-002.yml")


def test_profile_failure_is_captured_despite_github_errexit():
    workflow = WORKFLOW.read_text(encoding="utf-8")

    command = "set +e\n            resonance-corpus-campaign-step"
    capture = "local code=$?\n            set -e"

    assert command in workflow
    assert capture in workflow
    assert workflow.index(command) < workflow.index(capture)


def test_campaign_002_uses_jitter_tolerant_micro_notional_measurement():
    workflow = WORKFLOW.read_text(encoding="utf-8")

    assert "--campaign-id corpus-campaign-002" in workflow
    assert "--rolling-samples 6" in workflow
    assert "--rolling-horizon-ms 10000" in workflow
    assert "--rolling-min-coverage-ratio 0.5" in workflow
    assert "run_profile eth-usd 25" in workflow
    assert "run_profile ada-capacity-stress 250000" in workflow
    assert "data/corpus-campaign-002" in workflow


def test_campaign_001_workflow_is_frozen_not_scheduled():
    assert not Path(".github/workflows/corpus-campaign-001.yml").exists()
