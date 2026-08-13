from __future__ import annotations

import argparse
import json
from pathlib import Path

from .replay import ReplayBundle, benchmark_bundle, threshold_sensitivity


def _float_list(value: str) -> list[float]:
    try:
        values = [float(item.strip()) for item in value.split(",") if item.strip()]
    except ValueError as exc:
        raise argparse.ArgumentTypeError("threshold list must contain numbers") from exc
    if not values:
        raise argparse.ArgumentTypeError("threshold list cannot be empty")
    return values


def main() -> int:
    parser = argparse.ArgumentParser(
        description="RESONANCE offline paper-only market-state replay benchmark"
    )
    parser.add_argument("bundle", type=Path, help="JSON replay-bundle envelope")
    parser.add_argument(
        "--execute-threshold-bps",
        type=_float_list,
        default=None,
        help="optional comma-separated advisory execute thresholds",
    )
    parser.add_argument(
        "--volatile-threshold-bps",
        type=_float_list,
        default=None,
        help="optional comma-separated advisory volatility thresholds",
    )
    args = parser.parse_args()

    envelope = json.loads(args.bundle.read_text(encoding="utf-8"))
    bundle = ReplayBundle.from_envelope(envelope)
    report = benchmark_bundle(bundle)

    output = {
        "paper_only": True,
        "offline_replay": True,
        "report": report.to_envelope(),
    }
    if args.execute_threshold_bps is not None or args.volatile_threshold_bps is not None:
        if args.execute_threshold_bps is None or args.volatile_threshold_bps is None:
            parser.error(
                "--execute-threshold-bps and --volatile-threshold-bps must be supplied together"
            )
        output["threshold_sensitivity"] = [
            point.to_payload()
            for point in threshold_sensitivity(
                bundle,
                execute_net_edge_bps=args.execute_threshold_bps,
                volatile_return_bps=args.volatile_threshold_bps,
            )
        ]

    print(json.dumps(output, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
