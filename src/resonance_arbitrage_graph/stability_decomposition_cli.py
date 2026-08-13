from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from .holdout import HoldoutPolicy
from .joint_holdout import JointCandidateGrid, JointHoldoutPolicy
from .replay import ReplayBundle
from .stability_decomposition import StabilityDecompositionPolicy, run_stability_decomposition
from .walk_forward import WalkForwardPolicy, run_walk_forward_stability


def _csv_floats(value: str) -> tuple[float, ...]:
    try:
        values = tuple(float(item.strip()) for item in value.split(",") if item.strip())
    except ValueError as exc:
        raise argparse.ArgumentTypeError("expected comma-separated numbers") from exc
    if not values:
        raise argparse.ArgumentTypeError("expected at least one numeric value")
    return values


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Offline post-hoc decomposition of temporal walk-forward instability into evidence-bound diagnostic drift drivers.")
    parser.add_argument("bundle", type=Path, help="local replay-bundle envelope JSON")
    parser.add_argument("--execute-threshold-bps", type=_csv_floats, required=True)
    parser.add_argument("--volatile-threshold-bps", type=_csv_floats, required=True)
    parser.add_argument("--initial-calibration-operations", type=int, required=True)
    parser.add_argument("--validation-operations", type=int, required=True)
    parser.add_argument("--min-folds", type=int, default=3)
    parser.add_argument("--min-selected-policy-folds", type=int, default=2)
    parser.add_argument("--min-validation-pass-rate", type=float, default=2.0 / 3.0)
    parser.add_argument("--max-policy-switch-rate", type=float, default=0.5)
    parser.add_argument("--min-calibration-truth-events", type=int, required=True)
    parser.add_argument("--min-validation-truth-events", type=int, required=True)
    parser.add_argument("--min-truth-lower-bound", type=float, required=True)
    parser.add_argument("--min-survival-lower-bound", type=float, required=True)
    parser.add_argument("--min-calibration-execute-causal-changes", type=int, default=1)
    parser.add_argument("--min-calibration-volatility-causal-changes", type=int, default=1)
    parser.add_argument("--min-validation-execute-causal-changes", type=int, default=1)
    parser.add_argument("--min-validation-volatility-causal-changes", type=int, default=1)
    parser.add_argument("--confidence-z", type=float, default=1.96)
    parser.add_argument("--min-diagnostic-operations-per-side", type=int, default=2)
    parser.add_argument("--regime-tv-threshold", type=float, required=True)
    parser.add_argument("--route-tv-threshold", type=float, required=True)
    parser.add_argument("--capacity-drop-fraction-threshold", type=float, required=True)
    parser.add_argument("--quote-age-increase-ms-threshold", type=float, required=True)
    parser.add_argument("--overprediction-increase-bps-threshold", type=float, required=True)
    parser.add_argument("--causal-support-rate-drop-threshold", type=float, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    envelope = json.loads(args.bundle.read_text(encoding="utf-8"))
    bundle = ReplayBundle.from_envelope(envelope)
    grid = JointCandidateGrid(execute_net_edge_bps=args.execute_threshold_bps, volatile_return_bps=args.volatile_threshold_bps)
    first_fold_fraction = args.validation_operations / (args.initial_calibration_operations + args.validation_operations)
    holdout = HoldoutPolicy(
        validation_fraction=first_fold_fraction,
        min_calibration_operations=args.initial_calibration_operations,
        min_validation_operations=args.validation_operations,
        min_calibration_truth_events=args.min_calibration_truth_events,
        min_validation_truth_events=args.min_validation_truth_events,
        min_truth_rate_lower_bound=args.min_truth_lower_bound,
        min_survival_rate_lower_bound=args.min_survival_lower_bound,
        confidence_z=args.confidence_z,
    )
    joint = JointHoldoutPolicy(
        holdout=holdout,
        min_calibration_execute_causal_changes=args.min_calibration_execute_causal_changes,
        min_calibration_volatility_causal_changes=args.min_calibration_volatility_causal_changes,
        min_validation_execute_causal_changes=args.min_validation_execute_causal_changes,
        min_validation_volatility_causal_changes=args.min_validation_volatility_causal_changes,
    )
    walk_policy = WalkForwardPolicy(
        joint_policy=joint,
        initial_calibration_operations=args.initial_calibration_operations,
        validation_operations=args.validation_operations,
        min_folds=args.min_folds,
        min_selected_policy_folds=args.min_selected_policy_folds,
        min_validation_pass_rate=args.min_validation_pass_rate,
        max_policy_switch_rate=args.max_policy_switch_rate,
    )
    walk_report = run_walk_forward_stability(bundle, grid, walk_policy)
    decomposition_policy = StabilityDecompositionPolicy(
        min_operations_per_side=args.min_diagnostic_operations_per_side,
        regime_tv_threshold=args.regime_tv_threshold,
        route_tv_threshold=args.route_tv_threshold,
        capacity_ratio_drop_fraction_threshold=args.capacity_drop_fraction_threshold,
        quote_age_increase_ms_threshold=args.quote_age_increase_ms_threshold,
        overprediction_penalty_increase_bps_threshold=args.overprediction_increase_bps_threshold,
        causal_support_rate_drop_threshold=args.causal_support_rate_drop_threshold,
    )
    report = run_stability_decomposition(bundle, walk_report, decomposition_policy)
    print(json.dumps(report.to_envelope(), sort_keys=True, indent=2, ensure_ascii=False, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
