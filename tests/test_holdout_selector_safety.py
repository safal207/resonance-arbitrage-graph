from resonance_arbitrage_graph.holdout import (
    PolicyCandidate,
    PolicyEvaluation,
    _selection_key,
)
from resonance_arbitrage_graph.replay import ReplayMetrics


def _metrics(*, indeterminate: int) -> ReplayMetrics:
    return ReplayMetrics(
        logical_operations=10,
        true_positive=8,
        false_positive=2,
        expired=0,
        rejected=0,
        indeterminate=indeterminate,
        opportunity_truth_rate=0.8,
        false_opportunity_rate=0.2,
        route_survival_rate=1.0,
        mean_prediction_error_bps=-2.0,
    )


def _evaluation(
    threshold: float,
    *,
    indeterminate: int,
    execute_sim_count: int,
) -> PolicyEvaluation:
    return PolicyEvaluation(
        candidate=PolicyCandidate(execute_net_edge_bps=threshold),
        metrics=_metrics(indeterminate=indeterminate),
        execute_sim_count=execute_sim_count,
        truth_events=10,
        survival_events=10,
        truth_rate_lower_bound=0.70,
        survival_rate_lower_bound=0.90,
        overprediction_penalty_bps=2.0,
        results_sha256="0" * 64,
        eligible=True,
        reasons=(),
    )


def test_equal_evidence_does_not_reward_extra_indeterminate_execute_signals():
    noisy = _evaluation(20.0, indeterminate=3, execute_sim_count=13)
    resolved = _evaluation(40.0, indeterminate=0, execute_sim_count=10)

    assert sorted((noisy, resolved), key=_selection_key)[0] is resolved


def test_equal_resolved_evidence_prefers_more_conservative_execute_threshold():
    lower = _evaluation(20.0, indeterminate=0, execute_sim_count=10)
    higher = _evaluation(40.0, indeterminate=0, execute_sim_count=10)

    assert sorted((lower, higher), key=_selection_key)[0] is higher
