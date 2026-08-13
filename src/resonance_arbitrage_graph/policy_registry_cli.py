from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from .policy_registry import PolicyRegistry, verify_policy_registry_envelope


def _read(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Offline append-only lineage and revocation registry for promoted paper policies."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init", help="create a registry from a promoted policy receipt")
    init.add_argument("promotion", type=Path)
    init.add_argument("--reason", default="initial promoted policy release")

    supersede = sub.add_parser("supersede", help="append a promoted successor release")
    supersede.add_argument("registry", type=Path)
    supersede.add_argument("promotion", type=Path)
    supersede.add_argument("--reason", required=True)

    revoke = sub.add_parser("revoke", help="append a terminal revocation event")
    revoke.add_argument("registry", type=Path)
    revoke.add_argument("--reason", required=True)
    revoke.add_argument("--evidence-sha256", required=True)

    verify = sub.add_parser("verify", help="verify registry canonical structure and event hash chain")
    verify.add_argument("registry", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "init":
        registry = PolicyRegistry.create(_read(args.promotion), reason=args.reason)
        output = registry.to_envelope()
    elif args.command == "supersede":
        registry = PolicyRegistry.from_envelope(_read(args.registry))
        output = registry.supersede(_read(args.promotion), reason=args.reason).to_envelope()
    elif args.command == "revoke":
        registry = PolicyRegistry.from_envelope(_read(args.registry))
        output = registry.revoke(
            reason=args.reason,
            evidence_sha256=args.evidence_sha256,
        ).to_envelope()
    else:
        output = verify_policy_registry_envelope(_read(args.registry))
    print(json.dumps(output, sort_keys=True, indent=2, ensure_ascii=False, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
