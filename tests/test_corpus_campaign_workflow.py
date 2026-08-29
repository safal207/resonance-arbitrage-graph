from pathlib import Path


def test_campaign_001_workflow_is_retired_in_favor_of_campaign_002():
    assert not Path(".github/workflows/corpus-campaign-001.yml").exists()
    assert Path(".github/workflows/corpus-campaign-002.yml").exists()
