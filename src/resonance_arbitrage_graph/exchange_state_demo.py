"""Offline admission replay for a synthetic exchange-state drift fixture.

No order or fill is produced. Arrival states are retrospective diagnostics;
they are never inputs to the pre-submission decision.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

from .engine import Policy, evaluate_route
from .market_evidence import make_market_evidence_receipt
from .model import Verdict
from .quotes import CostAssumption, QuoteSnapshot, quote_to_trade_edges


_SCHEMA = "resonance.synthetic-exchange-state-fixture/v1"
_RANK = {Verdict.REJECT.value: 0, Verdict.OBSERVE.value: 1, Verdict.EXECUTE_SIM.value: 2}
_SOURCE_FILES = (
    "engine.py", "evidence.py", "exchange_state_demo.py", "market_evidence.py",
    "model.py", "quotes.py", "validation.py",
)


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False)


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _time(value: Any, name: str) -> int:
    if type(value) is not int or value < 0:
        raise ValueError(f"{name} must be a non-negative integer")
    return value


def _evaluate(
    state: dict[str, Any], *, at_ms: int, route: list[dict[str, str]],
    amount: float, costs: CostAssumption, policy: Policy, operation_id: str,
) -> dict[str, Any]:
    observed = _time(state["observed_at_ms"], "observed_at_ms")
    if observed > at_ms:
        raise ValueError("future snapshot cannot be used for this decision")
    if not isinstance(state["state_id"], str) or not state["state_id"]:
        raise ValueError("state_id must be a non-empty string")
    if state["exchange_status"] not in {"TRADING", "HALTED", "UNKNOWN"}:
        raise ValueError("unsupported synthetic exchange_status")

    snapshots = [QuoteSnapshot(
        venue="SIMULATED", observed_at_ms=observed,
        source_url=f"fixture://quantilan-v1/{state['state_id']}/{quote['symbol']}",
        **quote,
    ) for quote in state["quotes"]]
    by_symbol = {snapshot.symbol: snapshot for snapshot in snapshots}
    if len(by_symbol) != len(snapshots):
        raise ValueError("duplicate snapshot symbol")
    if any(snapshot.bid_price > snapshot.ask_price for snapshot in snapshots):
        raise ValueError("crossed synthetic book is not supported")
    if not route:
        raise ValueError("route must not be empty")
    edges = []
    for leg in route:
        if leg["side"] not in {"BUY", "SELL"}:
            raise ValueError("route side must be BUY or SELL")
        if leg["symbol"] not in by_symbol:
            raise ValueError(f"missing snapshot: {leg['symbol']}")
        pair = quote_to_trade_edges(by_symbol[leg["symbol"]], costs, now_ms=at_ms)
        edges.append(pair[0 if leg["side"] == "BUY" else 1])

    result = evaluate_route(edges, amount, policy=policy)
    receipt = make_market_evidence_receipt(
        operation_id, edges, result, snapshots=snapshots, evaluation_time_ms=at_ms,
    )
    reasons = list(result.reasons)
    verdict = result.verdict.value
    # This explicit fixture-only status gate wraps the existing route engine.
    # It is not an exchange adapter or a new production execution permission.
    if state["exchange_status"] != "TRADING":
        verdict = Verdict.REJECT.value
        reasons.append(f"EXCHANGE_NOT_TRADING:{state['exchange_status']}")
    if verdict == Verdict.OBSERVE.value:
        reasons.append("BELOW_EXECUTE_THRESHOLD")

    return {
        "state_id": state["state_id"], "state_sha256": digest(state),
        "evaluation_time_ms": at_ms, "snapshot_age_ms": at_ms - observed,
        "exchange_status": state["exchange_status"],
        "verdict": verdict, "reasons": reasons,
        "modeled_net_edge_bps": result.net_edge * 10_000,
        "market_evidence": {"payload": receipt.payload, "sha256": receipt.sha256},
    }


def run_demo(fixture: dict[str, Any]) -> dict[str, Any]:
    """Replay explicit fixture states, returning a deterministic hashed report."""
    if fixture["schema"] != _SCHEMA or fixture["paper_only"] is not True:
        raise ValueError("only the supported paper-only synthetic fixture is accepted")
    if fixture["source_kind"] != "SYNTHETIC_FIXTURE":
        raise ValueError("source_kind must be SYNTHETIC_FIXTURE")
    # Reject non-finite JSON before constructing any evidence.
    fixture_sha256 = digest(fixture)
    initial_at = _time(fixture["initial_validation_at_ms"], "initial_validation_at_ms")
    policy = Policy(**fixture["policy"])
    costs = CostAssumption(**fixture["costs"])
    route = fixture["route"]
    amount = fixture["start_amount"]
    common = {"route": route, "amount": amount, "costs": costs, "policy": policy}
    initial = _evaluate(fixture["initial_state"], at_ms=initial_at,
                        operation_id="quantilan:initial", **common)
    scenarios = fixture["scenarios"]
    if not scenarios:
        raise ValueError("at least one scenario is required")
    seen = set()
    cases = []
    for scenario in scenarios:
        case_id = scenario["id"]
        if not isinstance(case_id, str) or not case_id or case_id in seen:
            raise ValueError("scenario IDs must be unique non-empty strings")
        seen.add(case_id)
        boundary_at = _time(scenario["submission_at_ms"], "submission_at_ms")
        arrival_at = _time(scenario["arrival_at_ms"], "arrival_at_ms")
        if not initial_at <= boundary_at <= arrival_at:
            raise ValueError("timeline must satisfy initial <= submission <= arrival")

        boundary = _evaluate(scenario["boundary_state"], at_ms=boundary_at,
                             operation_id=f"quantilan:{case_id}:boundary", **common)
        # A failed/observe-only initial decision cannot be upgraded by replay.
        final_verdict = min((initial["verdict"], boundary["verdict"]), key=_RANK.__getitem__)
        final_reasons = list(boundary["reasons"])
        if initial["verdict"] != Verdict.EXECUTE_SIM.value:
            final_reasons.append(f"INITIAL_VERDICT:{initial['verdict']}")
        guarded_submits = final_verdict == Verdict.EXECUTE_SIM.value
        baseline_submits = initial["verdict"] == Verdict.EXECUTE_SIM.value

        # Deliberately evaluated AFTER the submission decision. This is a
        # hindsight diagnostic, not privileged future data used by the guard.
        arrival = _evaluate(scenario["arrival_state"], at_ms=arrival_at,
                            operation_id=f"quantilan:{case_id}:arrival-diagnostic", **common)
        arrival_permits = arrival["verdict"] == Verdict.EXECUTE_SIM.value
        cases.append({
            "id": case_id, "description": scenario["description"],
            "timing": {
                "initial_validation_at_ms": initial_at,
                "boundary_check_and_simulated_submission_at_ms": boundary_at,
                "simulated_arrival_at_ms": arrival_at,
                "initial_check_to_submission_ms": boundary_at - initial_at,
                "unprotected_submission_to_arrival_ms": arrival_at - boundary_at,
            },
            "reuse_initial_permission": {
                "verdict": initial["verdict"], "simulated_submission": baseline_submits,
                "decision_state_sha256": initial["state_sha256"],
            },
            "boundary_recheck": boundary,
            "guarded": {"verdict": final_verdict, "reasons": final_reasons,
                        "simulated_submission": guarded_submits,
                        "decision_state_sha256": boundary["state_sha256"]},
            "arrival_diagnostic": arrival,
            "comparison": {
                "reused_permission_disagrees_with_arrival_policy": baseline_submits and not arrival_permits,
                "guarded_submission_disagrees_with_arrival_policy": guarded_submits and not arrival_permits,
            },
        })

    source_dir = Path(__file__).parent
    payload = {
        "schema": "resonance.exchange-state-demo-report/v1", "paper_only": True,
        "source_kind": "SYNTHETIC_FIXTURE", "claim_status": "UNASSESSED_REPLAY_SOURCE",
        "fill_model": "NONE_ADMISSION_ONLY",
        "fixture_sha256": fixture_sha256,
        "implementation_files_sha256": {
            name: hashlib.sha256((source_dir / name).read_bytes()).hexdigest()
            for name in _SOURCE_FILES
        },
        "policy": asdict(policy), "costs": asdict(costs),
        "route": route, "start_amount": amount,
        "initial_validation": initial, "scenarios": cases,
        "limits": [
            "All market states and clock values are synthetic; no exchange is contacted.",
            "Top-of-book capacity only; no multi-level fills, queue position or partial fills.",
            "EXECUTE_SIM authorizes only an in-memory admission event, never a live order.",
            "Initial-to-submission delay is distinct from engine route latency (zero here).",
            "The recheck and simulated submission share one fixture clock tick.",
            "State may change after the last observation or after submission; no atomic exchange binding.",
            "Arrival diagnostics are hindsight policy checks, not observed fills or trading outcomes.",
            "Hashes identify inputs and implementation bytes; they do not authenticate market truth.",
        ],
    }
    return {"payload": payload, "sha256": digest(payload)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", required=True, type=Path)
    parser.add_argument("--output", type=Path, help="Write JSON report (default: stdout)")
    parser.add_argument("--check", type=Path, help="Compare with a saved report; exit 1 on mismatch")
    args = parser.parse_args(argv)
    try:
        report = run_demo(json.loads(args.fixture.read_text(encoding="utf-8")))
        if args.check is not None:
            expected = json.loads(args.check.read_text(encoding="utf-8"))
            if canonical_json(report) != canonical_json(expected):
                print("Report mismatch: fixture, implementation or results differ.", file=sys.stderr)
                return 1
            print(f"Replay matches: {report['sha256']}", file=sys.stderr)
        if args.output is not None:
            args.output.write_text(json.dumps(report, ensure_ascii=False, sort_keys=True,
                                             indent=2, allow_nan=False) + "\n", encoding="utf-8")
        elif args.check is None:
            print(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"Demo input/report error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
