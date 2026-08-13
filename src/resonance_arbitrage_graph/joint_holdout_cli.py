from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from .holdout import HoldoutPolicy
from .joint_holdout import (
    JointCandidateGrid,
    JointHoldoutPolicy,
    run_joint_holdout_calibration,
)
from .replay import ReplayBundle


def _csv_floats(value: str) -> tuple[float, ...]:
    try:
        values = tuple(float(item.strip()) for item in value.split(",") if item.strip())
    except ValueError as exc:
        raise argparse.ArgumentTypeError("expected comma-separated numbers") from exc
    if not values:
        raise argparse.ArgumentTypeError("expected at least one numeric value")
    return values


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Offline joint holdout calibration for execute and volatility thresholds "
            "with final-verdict causal-support guardrails."
        )
    )
    parser.add_argument("bundle", type=Path, help="local replay-bundle envelope JSON")
    parser.add_argument("--validation-fraction", type=float, required=True)
    parser.add_argument("--execute-threshold-bps", type=_csv_floats, required=True)
    parser.add_argument("--volatile-threshold-bps", type=_csv_floats, required=True)
    parser.add_argument("--min-calibration-operations", type=int, required=True)
    parser.add_argument("--min-validation-operations", type=int, required=True)
    parser.add_argument("--min-calibration-truth-events", type=int, required=True)
    parser.add_argument("--min-validation-truth-events", type=int, required=True)
    parser.add_argument("--min-truth-lower-bound", type=float, required=True)
    parser.add_argument("--min-survival-lower-bound", type=float, required=True)
    parser.add_argument("--min-calibration-execute-causal-changes", type=int, default=1)
    parser.add_argument("--min-calibration-volatility-causal-changes", type=int, default=1)
    parser.add_argument("--min-validation-execute-causal-changes", type=int, default=1)
    parser.add_argument("--min-validation-volatility-causal-changes", type=int, default=1)
    parser.add_argument("--confidence-z", type=float, default=1.96)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    envelope = json.loads(args.bundle.read_text(encoding="utf-8"))
    bundle = ReplayBundle.from_envelope(envelope)
    grid = JointCandidateGrid(
        execute_net_edge_bps=args.execute_threshold_bps,
        volatile_return_bps=args.volatile_threshold_bps,
    )
    holdout = HoldoutPolicy(
        validation_fraction=args.validation_fraction,
        min_calibration_operations=args.min_calibration_operations,
        min_validation_operations=args.min_validation_operations,
        min_calibration_truth_events=args.min_calibration_truth_events,
        min_validation_truth_events=args.min_validation_truth_events,
        min_truth_rate_lower_bound=args.min_truth_lower_bound,
        min_survival_rate_lower_bound=args.min_survival_lower_bound,
        confidence_z=args.confidence_z,
    )
    policy = JointHoldoutPolicy(
        holdout=holdout,
        min_calibration_execute_causal_changes=args.min_calibration_execute_causal_changes,
        min_calibration_volatility_causal_changes=args.min_calibration_volatility_causal_changes,
        min_validation_execute_causal_changes=args.min_validation_execute_causal_changes,
        min_validation_volatility_causal_changes=args.min_validation_volatility_causal_changes,
    )
    report = run_joint_holdout_calibration(bundle, grid, policy)
    print(
        json.dumps(
            report.to_envelope(),
            sort_keys=True,
            indent=2,
            ensure_ascii=False,
            allow_nan=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
