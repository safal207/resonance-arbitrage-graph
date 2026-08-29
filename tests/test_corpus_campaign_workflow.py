from pathlib import Path


def test_profile_failure_is_captured_despite_github_errexit():
    workflow = Path(".github/workflows/corpus-campaign-001.yml").read_text(
        encoding="utf-8"
    )

    command = "set +e\n            resonance-corpus-campaign-step"
    capture = "local code=$?\n            set -e"

    assert command in workflow
    assert capture in workflow
    assert workflow.index(command) < workflow.index(capture)
