from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from .holdout import CandidateGrid, HoldoutPolicy, run_holdout_calibration
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
        description="Offline holdout policy calibration for replay bundles. No network or execution path."
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
    parser.add_argument("--confidence-z", type=float, default=1.96)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    envelope = json.loads(args.bundle.read_text(encoding="utf-8"))
    bundle = ReplayBundle.from_envelope(envelope)
    grid = CandidateGrid(
        execute_net_edge_bps=args.execute_threshold_bps,
        volatile_return_bps=args.volatile_threshold_bps,
    )
    policy = HoldoutPolicy(
        validation_fraction=args.validation_fraction,
        min_calibration_operations=args.min_calibration_operations,
        min_validation_operations=args.min_validation_operations,
        min_calibration_truth_events=args.min_calibration_truth_events,
        min_validation_truth_events=args.min_validation_truth_events,
        min_truth_rate_lower_bound=args.min_truth_lower_bound,
        min_survival_rate_lower_bound=args.min_survival_lower_bound,
        confidence_z=args.confidence_z,
    )
    report = run_holdout_calibration(bundle, grid, policy)
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
