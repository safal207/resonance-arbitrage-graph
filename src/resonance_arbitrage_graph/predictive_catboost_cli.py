from __future__ import annotations

import argparse
import json
from pathlib import Path

from .predictive import build_predictive_dataset
from .predictive_catboost import CatBoostResearchConfig, run_catboost_walk_forward
from .replay import ReplayBundle


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run paper-only expanding walk-forward CatBoost comparison "
            "against the historical-mean predictive baseline."
        )
    )
    parser.add_argument("replay_bundle", type=Path)
    parser.add_argument("--min-training-rows", type=int, default=20)
    parser.add_argument("--iterations", type=int, default=64)
    parser.add_argument("--depth", type=int, default=4)
    parser.add_argument("--learning-rate", type=float, default=0.05)
    parser.add_argument("--l2-leaf-reg", type=float, default=3.0)
    parser.add_argument("--random-seed", type=int, default=207)
    parser.add_argument("--thread-count", type=int, default=1)
    parser.add_argument("--min-survival-probability", type=float, default=0.50)
    parser.add_argument(
        "--min-positive-realized-pnl-probability",
        type=float,
        default=0.50,
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    envelope = json.loads(args.replay_bundle.read_text(encoding="utf-8"))
    bundle = ReplayBundle.from_envelope(envelope)
    dataset = build_predictive_dataset(bundle)
    config = CatBoostResearchConfig(
        iterations=args.iterations,
        depth=args.depth,
        learning_rate=args.learning_rate,
        l2_leaf_reg=args.l2_leaf_reg,
        random_seed=args.random_seed,
        thread_count=args.thread_count,
    )
    comparison = run_catboost_walk_forward(
        dataset,
        config=config,
        min_training_rows=args.min_training_rows,
        min_survival_probability=args.min_survival_probability,
        min_positive_realized_pnl_probability=(
            args.min_positive_realized_pnl_probability
        ),
    )
    print(
        json.dumps(
            {
                "payload": comparison.to_payload(),
                "sha256": comparison.sha256,
            },
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
