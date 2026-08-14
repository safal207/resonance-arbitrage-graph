from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .policy_authority import (
    PolicyAuthorityAction,
    PolicyAuthorityLedger,
    PolicyAuthorizationReceipt,
    authorize_registry_event,
    make_policy_authority_registry_receipt,
    verify_policy_authority_ledger_envelope,
    verify_policy_authorization_binding,
    verify_policy_authorization_receipt_envelope,
)
from .policy_authority_verification import (
    verify_policy_authority_registry_receipt_envelope,
)
from .policy_registry import PolicyRegistry


def _load(path: str) -> dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _write(payload: dict[str, Any], output: str | None) -> None:
    rendered = json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=False) + "\n"
    if output:
        Path(output).write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")


def _actions(value: str) -> tuple[PolicyAuthorityAction, ...]:
    raw = tuple(part.strip() for part in value.split(",") if part.strip())
    if not raw:
        raise argparse.ArgumentTypeError("at least one action is required")
    try:
        return tuple(PolicyAuthorityAction(item.upper()) for item in raw)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("actions must be RELEASE,SUPERSEDE,REVOKE") from exc


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="resonance-policy-authority",
        description="Offline evidence-bound policy authority and delegation receipts.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    bootstrap = sub.add_parser("bootstrap")
    bootstrap.add_argument("--authority-id", required=True)
    bootstrap.add_argument("--authority-basis", required=True)
    bootstrap.add_argument("--policy-context-sha256", required=True)
    bootstrap.add_argument("--actions", required=True, type=_actions)
    bootstrap.add_argument("--evidence-sha256", required=True)
    bootstrap.add_argument("--reason", default="bootstrap root policy authority")
    bootstrap.add_argument("--output")

    delegate = sub.add_parser("delegate")
    delegate.add_argument("--ledger", required=True)
    delegate.add_argument("--parent-grant-id", required=True)
    delegate.add_argument("--authority-id", required=True)
    delegate.add_argument("--authority-basis", required=True)
    delegate.add_argument("--actions", required=True, type=_actions)
    delegate.add_argument("--evidence-sha256", required=True)
    delegate.add_argument("--reason", required=True)
    delegate.add_argument("--output")

    revoke = sub.add_parser("revoke-grant")
    revoke.add_argument("--ledger", required=True)
    revoke.add_argument("--grant-id", required=True)
    revoke.add_argument("--reason", required=True)
    revoke.add_argument("--evidence-sha256", required=True)
    revoke.add_argument("--output")

    authorize = sub.add_parser("authorize")
    authorize.add_argument("--ledger", required=True)
    authorize.add_argument("--registry", required=True)
    authorize.add_argument("--grant-id", required=True)
    authorize.add_argument("--event-sequence", required=True, type=int)
    authorize.add_argument("--evidence-sha256", required=True)
    authorize.add_argument("--output")

    verify_ledger = sub.add_parser("verify-ledger")
    verify_ledger.add_argument("--ledger", required=True)

    verify_auth = sub.add_parser("verify-authorization")
    verify_auth.add_argument("--authorization", required=True)
    verify_auth.add_argument("--ledger", required=True)
    verify_auth.add_argument("--registry", required=True)

    receipt = sub.add_parser("registry-receipt")
    receipt.add_argument("--registry", required=True)
    receipt.add_argument("--authorization", action="append", required=True)
    receipt.add_argument("--output")

    verify_receipt = sub.add_parser("verify-registry-receipt")
    verify_receipt.add_argument("--receipt", required=True)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)

    if args.command == "bootstrap":
        ledger = PolicyAuthorityLedger.bootstrap(
            authority_id=args.authority_id,
            authority_basis=args.authority_basis,
            policy_context_sha256=args.policy_context_sha256,
            actions=args.actions,
            evidence_sha256=args.evidence_sha256,
            reason=args.reason,
        )
        _write(ledger.to_envelope(), args.output)
        return 0

    if args.command == "delegate":
        ledger = PolicyAuthorityLedger.from_envelope(_load(args.ledger))
        updated = ledger.delegate(
            parent_grant_id=args.parent_grant_id,
            authority_id=args.authority_id,
            authority_basis=args.authority_basis,
            actions=args.actions,
            evidence_sha256=args.evidence_sha256,
            reason=args.reason,
        )
        _write(updated.to_envelope(), args.output)
        return 0

    if args.command == "revoke-grant":
        ledger = PolicyAuthorityLedger.from_envelope(_load(args.ledger))
        updated = ledger.revoke_grant(
            args.grant_id,
            reason=args.reason,
            evidence_sha256=args.evidence_sha256,
        )
        _write(updated.to_envelope(), args.output)
        return 0

    if args.command == "authorize":
        ledger = PolicyAuthorityLedger.from_envelope(_load(args.ledger))
        registry = PolicyRegistry.from_envelope(_load(args.registry))
        authorization = authorize_registry_event(
            ledger,
            registry,
            grant_id=args.grant_id,
            registry_event_sequence=args.event_sequence,
            evidence_sha256=args.evidence_sha256,
        )
        _write(authorization.to_envelope(), args.output)
        return 0

    if args.command == "verify-ledger":
        verify_policy_authority_ledger_envelope(_load(args.ledger))
        print("OK")
        return 0

    if args.command == "verify-authorization":
        authorization = _load(args.authorization)
        verify_policy_authorization_receipt_envelope(authorization)
        verify_policy_authorization_binding(
            authorization,
            _load(args.ledger),
            _load(args.registry),
        )
        print("OK")
        return 0

    if args.command == "registry-receipt":
        registry = PolicyRegistry.from_envelope(_load(args.registry))
        authorizations = tuple(
            PolicyAuthorizationReceipt.from_envelope(_load(path))
            for path in args.authorization
        )
        result = make_policy_authority_registry_receipt(registry, authorizations)
        _write(result.to_envelope(), args.output)
        return 0

    if args.command == "verify-registry-receipt":
        verify_policy_authority_registry_receipt_envelope(_load(args.receipt))
        print("OK")
        return 0

    raise RuntimeError("unreachable command")


if __name__ == "__main__":
    raise SystemExit(main())
