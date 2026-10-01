"""Standard-library tests, also collected by the repository's pytest suite."""

from contextlib import redirect_stderr
from copy import deepcopy
from io import StringIO
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from resonance_arbitrage_graph.exchange_state_demo import canonical_json, digest, main, run_demo


DEMO = Path(__file__).resolve().parents[1] / "examples" / "quantilan"


def cases(report):
    return {case["id"]: case for case in report["payload"]["scenarios"]}


class ExchangeStateDemoTests(unittest.TestCase):
    def setUp(self):
        self.fixture = json.loads((DEMO / "fixture.json").read_text())

    def test_frozen_fixture_replays_offline_without_mutation(self):
        original = deepcopy(self.fixture)
        with patch("socket.socket", side_effect=AssertionError("network access")):
            first = run_demo(self.fixture)
            self.assertEqual(self.fixture, original)
            self.assertEqual(first, run_demo(self.fixture))
        expected = json.loads((DEMO / "expected-report.json").read_text())
        self.assertEqual(canonical_json(first), canonical_json(expected))
        self.assertEqual(first["sha256"], digest(first["payload"]))
        self.assertEqual(first["payload"]["fixture_sha256"], digest(self.fixture))
        self.assertEqual(first["payload"]["claim_status"], "UNASSESSED_REPLAY_SOURCE")
        self.assertEqual(first["payload"]["fill_model"], "NONE_ADMISSION_ONLY")

    def test_positive_control_and_pre_submission_drift(self):
        report = run_demo(self.fixture)
        self.assertEqual(report["payload"]["initial_validation"]["verdict"], "EXECUTE_SIM")
        rows = cases(report)
        self.assertTrue(rows["unchanged_fresh"]["guarded"]["simulated_submission"])
        self.assertEqual(rows["unchanged_fresh"]["arrival_diagnostic"]["verdict"], "EXECUTE_SIM")
        expected = {
            "depth_shrink": ("REJECT", "CAPACITY_EXCEEDED:0"),
            "price_drift": ("REJECT", "NON_POSITIVE_NET_EDGE"),
            "edge_below_threshold": ("OBSERVE", "BELOW_EXECUTE_THRESHOLD"),
            "exchange_halted": ("REJECT", "EXCHANGE_NOT_TRADING:HALTED"),
            "stale_snapshot": ("REJECT", "STALE_QUOTE:0"),
        }
        for name, (verdict, reason) in expected.items():
            with self.subTest(scenario=name):
                row = rows[name]
                self.assertTrue(row["reuse_initial_permission"]["simulated_submission"])
                self.assertEqual(row["guarded"]["verdict"], verdict)
                self.assertIn(reason, row["guarded"]["reasons"])
                self.assertFalse(row["guarded"]["simulated_submission"])
        self.assertEqual(rows["depth_shrink"]["boundary_recheck"]["snapshot_age_ms"], 5)
        self.assertGreater(rows["depth_shrink"]["boundary_recheck"]["modeled_net_edge_bps"], 30)
        edge = rows["edge_below_threshold"]["boundary_recheck"]["modeled_net_edge_bps"]
        self.assertGreater(edge, 0)
        self.assertLess(edge, 30)

    def test_post_check_drift_is_a_remaining_race(self):
        row = cases(run_demo(self.fixture))["drift_after_recheck"]
        self.assertTrue(row["guarded"]["simulated_submission"])
        self.assertEqual(row["arrival_diagnostic"]["verdict"], "REJECT")
        self.assertIn("CAPACITY_EXCEEDED:0", row["arrival_diagnostic"]["reasons"])
        self.assertTrue(row["comparison"]["guarded_submission_disagrees_with_arrival_policy"])
        self.assertEqual(row["timing"]["unprotected_submission_to_arrival_ms"], 20)

    def test_arrival_data_cannot_change_submission_decision(self):
        before = cases(run_demo(self.fixture))["unchanged_fresh"]
        self.fixture["scenarios"][0]["arrival_state"]["exchange_status"] = "HALTED"
        after = cases(run_demo(self.fixture))["unchanged_fresh"]
        self.assertEqual(before["guarded"], after["guarded"])
        self.assertEqual(before["boundary_recheck"], after["boundary_recheck"])
        self.assertNotEqual(before["arrival_diagnostic"], after["arrival_diagnostic"])
        self.assertTrue(after["comparison"]["guarded_submission_disagrees_with_arrival_policy"])

    def test_initial_permission_cannot_be_upgraded(self):
        for change, expected in [("capacity", "REJECT"), ("price", "OBSERVE")]:
            with self.subTest(initial_change=change):
                fixture = deepcopy(self.fixture)
                if change == "capacity":
                    fixture["initial_state"]["quotes"][0]["ask_qty"] = 0.0075
                else:
                    fixture["initial_state"]["quotes"][2]["bid_price"] = 4020.0
                row = cases(run_demo(fixture))["unchanged_fresh"]
                self.assertEqual(row["boundary_recheck"]["verdict"], "EXECUTE_SIM")
                self.assertEqual(row["guarded"]["verdict"], expected)
                self.assertFalse(row["guarded"]["simulated_submission"])

    def test_second_leg_capacity_uses_its_input_asset(self):
        self.fixture["scenarios"][0]["boundary_state"]["quotes"][1]["ask_qty"] = 0.1
        row = cases(run_demo(self.fixture))["unchanged_fresh"]
        self.assertEqual(row["guarded"]["verdict"], "REJECT")
        self.assertIn("CAPACITY_EXCEEDED:1", row["guarded"]["reasons"])

    def test_freshness_limit_is_inclusive(self):
        state = self.fixture["scenarios"][0]["boundary_state"]
        state["observed_at_ms"] = 980  # 1080 - 980 == 100 ms
        self.assertEqual(cases(run_demo(self.fixture))["unchanged_fresh"]["guarded"]["verdict"], "EXECUTE_SIM")
        state["observed_at_ms"] = 979
        self.assertEqual(cases(run_demo(self.fixture))["unchanged_fresh"]["guarded"]["verdict"], "REJECT")

    def test_evidence_binds_current_price_capacity_and_age(self):
        report = run_demo(self.fixture)
        for row in report["payload"]["scenarios"]:
            for phase in ("boundary_recheck", "arrival_diagnostic"):
                receipt = row[phase]["market_evidence"]
                self.assertEqual(receipt["sha256"], digest(receipt["payload"]))
                evidence = receipt["payload"]
                self.assertEqual([binding["side"] for binding in evidence["market_bindings"]], ["BUY", "BUY", "SELL"])
                self.assertTrue(all(edge["quote_age_ms"] == row[phase]["snapshot_age_ms"] for edge in evidence["route"]))
        depth = cases(report)["depth_shrink"]["boundary_recheck"]["market_evidence"]["payload"]
        self.assertEqual(depth["route"][0]["capacity"], 600.0)
        self.assertEqual(depth["market_data"][0]["venue"], "SIMULATED")

    def test_unknown_exchange_status_blocks_submission(self):
        self.fixture["scenarios"][0]["boundary_state"]["exchange_status"] = "UNKNOWN"
        row = cases(run_demo(self.fixture))["unchanged_fresh"]
        self.assertEqual(row["guarded"]["verdict"], "REJECT")
        self.assertIn("EXCHANGE_NOT_TRADING:UNKNOWN", row["guarded"]["reasons"])

    def test_invalid_fixture_fails_closed(self):
        mutations = [
            (lambda f: f.update(paper_only=False), "paper-only"),
            (lambda f: f.update(source_kind="LIVE"), "SYNTHETIC_FIXTURE"),
            (lambda f: f["scenarios"][0]["boundary_state"].update(observed_at_ms=1081), "future snapshot"),
            (lambda f: f["scenarios"][0].update(arrival_at_ms=1079), "timeline"),
            (lambda f: f["scenarios"][0].update(submission_at_ms=True), "non-negative integer"),
            (lambda f: f["scenarios"][1].update(id=f["scenarios"][0]["id"]), "unique"),
            (lambda f: f["route"][0].update(side="UNKNOWN"), "route side"),
            (lambda f: f["scenarios"][0]["boundary_state"]["quotes"].pop(0), "missing snapshot"),
            (lambda f: f["scenarios"][0]["boundary_state"].update(exchange_status=""), "exchange_status"),
            (lambda f: f.update(start_amount=float("nan")), "JSON compliant"),
        ]
        for mutate, message in mutations:
            with self.subTest(rejected_input=message):
                fixture = deepcopy(self.fixture)
                mutate(fixture)
                with self.assertRaisesRegex(ValueError, message):
                    run_demo(fixture)

    def test_changed_policy_invalidates_replay_hash(self):
        before = run_demo(self.fixture)
        self.fixture["policy"]["execute_net_edge"] = 0.004
        after = run_demo(self.fixture)
        self.assertNotEqual(before["sha256"], after["sha256"])
        self.assertNotEqual(before["payload"]["fixture_sha256"], after["payload"]["fixture_sha256"])

    def test_cli_replay_check_and_tampered_report(self):
        fixture_path = str(DEMO / "fixture.json")
        with tempfile.TemporaryDirectory() as temp, redirect_stderr(StringIO()) as stderr:
            report_path = Path(temp) / "report.json"
            self.assertEqual(main(["--fixture", fixture_path, "--output", str(report_path)]), 0)
            self.assertEqual(main(["--fixture", fixture_path, "--check", str(report_path)]), 0)
            self.assertIn("Replay matches", stderr.getvalue())
            report = json.loads(report_path.read_text())
            report["payload"]["scenarios"][1]["guarded"]["simulated_submission"] = True
            report_path.write_text(json.dumps(report))
            self.assertEqual(main(["--fixture", fixture_path, "--check", str(report_path)]), 1)
            self.assertIn("mismatch", stderr.getvalue())
            self.assertEqual(main(["--fixture", str(Path(temp) / "missing.json")]), 2)


if __name__ == "__main__":
    unittest.main()
