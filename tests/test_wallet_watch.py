from copy import deepcopy
import io
import json
from unittest.mock import patch

import pytest

from resonance_arbitrage_graph.wallet_watch import (
    History, Monitor, Rpc, USDC, WatchError, format_usdc, usdc_units, verify_evidence,
)
from resonance_arbitrage_graph.wallet_watch_cli import main
from resonance_arbitrage_graph.wallet_watch_demo import DEMO_ADDRESS, DEMO_TX, FixtureRpc, fixture


def evidence():
    return {"chain_id": "0x1", **fixture()}


def open_monitor(tmp_path, rpc=None, minimum=1_000_000):
    history = History(tmp_path / "watch.sqlite3")
    return Monitor(rpc or FixtureRpc(), history, DEMO_ADDRESS, minimum_units=minimum), history


def test_whole_cli_demo_and_restart(tmp_path, capsys):
    db = str(tmp_path / "demo.sqlite3")
    assert main(["demo", "--db", db]) == 0
    lines = [json.loads(line) for line in capsys.readouterr().out.splitlines()]
    assert len(lines) == 2
    assert lines[0]["amount"] == "125.500000"
    assert lines[0]["direction"] == "incoming"
    assert lines[0]["origin"] == "SYNTHETIC_FIXTURE"
    assert lines[1]["history_events"] == 1
    assert lines[1]["restart_notifications"] == 0
    assert lines[1]["live_rpc_verified"] is False
    assert main(["demo", "--db", db]) == 0
    assert len(capsys.readouterr().out.splitlines()) == 1
    assert main(["history", "--db", db]) == 0
    saved = json.loads(capsys.readouterr().out)
    assert saved["notification"] == "console_emitted"
    assert saved["event"]["amount_units"] == "125500000"


@pytest.mark.parametrize("mutation", [
    lambda e: e.update(chain_id="0x89"),
    lambda e: e["log"].update(address="0x" + "99" * 20),
    lambda e: e["log"].update(removed=True),
    lambda e: e["log"].pop("removed"),
    lambda e: e["log"].update(data="0x01"),
    lambda e: e["log"].update(topics=e["log"]["topics"][:2]),
    lambda e: e["log"]["topics"].__setitem__(2, "0x" + "ff" * 32),
    lambda e: e["receipt"].update(status="0x0"),
    lambda e: e["receipt"].update(logs=[]),
    lambda e: e["receipt"]["logs"].append(deepcopy(e["receipt"]["logs"][0])),
    lambda e: e["receipt"].update(transactionHash="0x" + "99" * 32),
    lambda e: e["receipt"]["logs"][0].update(data="0x" + "00" * 32),
    lambda e: e["block"].update(hash="0x" + "99" * 32),
    lambda e: e["block"].update(number="0x65"),
    lambda e: e["finalized"].update(number="0x63"),
    lambda e: e["finalized"].update(number="0x64"),
    lambda e: e["finalized"].update(timestamp="0x1"),
])
def test_reject_inconsistent_evidence(mutation):
    item = evidence()
    mutation(item)
    with pytest.raises(WatchError):
        verify_evidence(item, DEMO_ADDRESS)


def test_unrelated_address_rejected():
    with pytest.raises(WatchError, match="does not involve"):
        verify_evidence(evidence(), "0x" + "33" * 20)


def test_exact_uint256_amount():
    units = 2**256 - 1
    assert usdc_units(format_usdc(units)) == units
    item = evidence()
    for log in (item["log"], item["receipt"]["logs"][0]):
        log["data"] = "0x" + f"{units:064x}"
    assert verify_evidence(item, DEMO_ADDRESS)["amount"] == format_usdc(units)


@pytest.mark.parametrize("value", ["-1", "NaN", "1e6", "0.0000001", "inf"])
def test_invalid_amounts(value):
    with pytest.raises(WatchError):
        usdc_units(value)


def test_failed_notification_is_pending_after_restart(tmp_path):
    monitor, history = open_monitor(tmp_path)
    assert monitor.transaction(DEMO_TX) == 1
    with pytest.raises(OSError):
        history.emit_pending(lambda _: (_ for _ in ()).throw(OSError("broken sink")))
    history.close()
    monitor, history = open_monitor(tmp_path)
    notifications = []
    assert monitor.transaction(DEMO_TX) == 0
    assert history.emit_pending(notifications.append) == 1
    assert history.emit_pending(notifications.append) == 0
    assert len(history.records()) == len(notifications) == 1
    history.close()


def test_zero_and_below_threshold_retained_without_notification(tmp_path):
    rpc = FixtureRpc()
    for log in (rpc.data["log"], rpc.data["receipt"]["logs"][0]):
        log["data"] = "0x" + "00" * 32
    monitor, history = open_monitor(tmp_path, rpc)
    assert monitor.transaction(DEMO_TX) == 1
    assert history.emit_pending(lambda _: pytest.fail("below threshold notification")) == 0
    assert history.records()[0]["notification"] == "below_threshold"
    history.close()


def test_self_transfer_seen_in_both_filters_is_one_event(tmp_path):
    rpc = FixtureRpc()
    for log in (rpc.data["log"], rpc.data["receipt"]["logs"][0]):
        log["topics"][1] = log["topics"][2]
    monitor, history = open_monitor(tmp_path, rpc)
    assert monitor.scan()["new_events"] == 1
    assert history.records()[0]["event"]["direction"] == "self"
    assert len([call for call in rpc.calls if call[0] == "eth_getLogs"]) == 2
    history.close()


def test_failed_verification_does_not_advance_or_store(tmp_path):
    rpc = FixtureRpc()
    rpc.data["receipt"]["status"] = "0x0"
    monitor, history = open_monitor(tmp_path, rpc)
    with pytest.raises(WatchError):
        monitor.scan()
    assert history.checkpoint() is None
    assert history.records() == []
    rpc.data["receipt"]["status"] = "0x1"
    assert monitor.scan()["new_events"] == 1
    history.close()


def test_rpc_failure_on_second_filter_keeps_checkpoint(tmp_path):
    class FailingRpc(FixtureRpc):
        def call(self, method, params):
            if method == "eth_getLogs" and len(params[0]["topics"]) == 3:
                raise WatchError("provider unavailable")
            return super().call(method, params)
    monitor, history = open_monitor(tmp_path, FailingRpc())
    with pytest.raises(WatchError):
        monitor.scan()
    assert history.checkpoint() is None and history.records() == []
    history.close()


def test_changed_finalized_checkpoint_stops(tmp_path):
    rpc = FixtureRpc()
    monitor, history = open_monitor(tmp_path, rpc)
    monitor.scan()
    checkpoint = history.checkpoint()
    rpc.data["finalized"]["hash"] = "0x" + "99" * 32
    with pytest.raises(WatchError, match="checkpoint changed"):
        monitor.scan()
    assert history.checkpoint() == checkpoint
    history.close()


def test_existing_checkpoint_prevents_rewind(tmp_path):
    monitor, history = open_monitor(tmp_path)
    monitor.scan()
    with pytest.raises(WatchError, match="omit --start-block"):
        monitor.scan(start_block=100)
    assert monitor.scan()["status"] == "caught_up"
    history.close()


def test_caught_up_empty_range_is_not_full_wallet_history(tmp_path):
    monitor, history = open_monitor(tmp_path)
    result = monitor.scan(start_block=105)
    assert result["new_events"] == 0
    assert result["from_block"] == 105
    assert result["through_block"] == 110
    assert "not independently proven" in result["coverage"]
    history.close()


def test_history_detects_modified_packet(tmp_path):
    monitor, history = open_monitor(tmp_path)
    monitor.transaction(DEMO_TX)
    row = history.db.execute("SELECT packet FROM events").fetchone()
    packet = json.loads(row[0])
    packet["event"]["amount"] = "9000.000000"
    with history.db:
        history.db.execute("UPDATE events SET packet=?", (json.dumps(packet),))
    with pytest.raises(WatchError, match="digest mismatch"):
        history.records()
    with pytest.raises(WatchError):
        history.emit_pending(lambda _: pytest.fail("corrupt notification"))
    history.close()


def test_database_identity_and_threshold_binding(tmp_path):
    _, history = open_monitor(tmp_path)
    with pytest.raises(WatchError):
        Monitor(FixtureRpc(), history, "0x" + "33" * 20)
    with pytest.raises(WatchError):
        Monitor(FixtureRpc(), history, DEMO_ADDRESS, minimum_units=2)
    rpc = FixtureRpc()
    rpc.origin = "LIVE_RPC"
    with pytest.raises(WatchError):
        Monitor(rpc, history, DEMO_ADDRESS)
    history.close()


def test_changed_event_and_stale_writer_roll_back(tmp_path):
    monitor, history = open_monitor(tmp_path)
    monitor.scan()
    rpc = FixtureRpc()
    for log in (rpc.data["log"], rpc.data["receipt"]["logs"][0]):
        log["data"] = "0x" + f"{2_000_000:064x}"
    with pytest.raises(WatchError, match="transfer changed"):
        Monitor(rpc, history, DEMO_ADDRESS).transaction(DEMO_TX)
    with pytest.raises(WatchError, match="Another scan"):
        history.save([], minimum=1_000_000, checkpoint=(120, "0x" + "00" * 32), expected=None)
    assert history.records()[0]["event"]["amount"] == "125.500000"
    assert history.checkpoint()[0] == 110
    history.close()


def test_rpc_write_methods_forbidden_and_errors_redacted():
    rpc = Rpc("https://rpc.example/private-secret?key=secret")
    with pytest.raises(WatchError, match="read-only"):
        rpc.call("eth_sendRawTransaction", ["0x00"])
    with patch("resonance_arbitrage_graph.wallet_watch.urlopen", side_effect=OSError("private-secret")):
        with pytest.raises(WatchError) as error:
            rpc.call("eth_chainId", [])
    assert "private-secret" not in str(error.value)


@pytest.mark.parametrize("body", [
    {"jsonrpc": "2.0", "id": 2, "result": "0x1"},
    {"jsonrpc": "2.0", "id": True, "result": "0x1"},
    {"jsonrpc": "2.0", "id": 1, "error": {"message": "secret"}},
    {"id": 1, "result": "0x1"},
])
def test_rpc_response_binding(body):
    with patch("resonance_arbitrage_graph.wallet_watch.urlopen", return_value=io.BytesIO(json.dumps(body).encode())):
        with pytest.raises(WatchError):
            Rpc("https://rpc.example").call("eth_chainId", [])


def test_missing_history_is_an_error(tmp_path):
    assert main(["history", "--db", str(tmp_path / "missing.sqlite3")]) == 2
    assert not (tmp_path / "missing.sqlite3").exists()


def test_multiple_transfers_in_one_transaction_remain_distinct(tmp_path):
    rpc = FixtureRpc()
    second = deepcopy(rpc.data["receipt"]["logs"][0])
    second["logIndex"] = "0x4"
    second["data"] = "0x" + f"{1_000_000:064x}"
    rpc.data["receipt"]["logs"].append(second)
    monitor, history = open_monitor(tmp_path, rpc)
    assert monitor.transaction(DEMO_TX) == 2
    notices = []
    assert history.emit_pending(notices.append) == 2
    assert len({notice["event_id"] for notice in notices}) == 2
    assert monitor.transaction(DEMO_TX) == 0
    history.close()


def test_finalized_view_change_during_scan_does_not_commit(tmp_path):
    class ChangingRpc(FixtureRpc):
        def call(self, method, params):
            value = super().call(method, params)
            if method == "eth_getBlockByNumber" and params[0] == "0x6e":
                value["hash"] = "0x" + "99" * 32
            return value
    monitor, history = open_monitor(tmp_path, ChangingRpc())
    with pytest.raises(WatchError, match="Finalized view changed"):
        monitor.scan()
    assert history.checkpoint() is None and history.records() == []
    history.close()


def test_failure_while_catching_up_retains_last_successful_range(tmp_path):
    monitor, history = open_monitor(tmp_path)
    assert monitor.scan(start_block=100, batch_size=1)["through_block"] == 100
    checkpoint = history.checkpoint()
    call = monitor.rpc.call
    def failing(method, params):
        return None if method == "eth_getLogs" else call(method, params)
    monitor.rpc.call = failing
    with pytest.raises(WatchError):
        monitor.scan()
    assert history.checkpoint() == checkpoint
    assert len(history.records()) == 1
    monitor.rpc.call = call
    assert monitor.scan()["from_block"] == 101
    assert history.checkpoint()[0] == 110
    history.close()


def test_receipt_cannot_smuggle_another_transaction(tmp_path):
    rpc = FixtureRpc()
    rpc.data["receipt"]["logs"][0]["transactionHash"] = "0x" + "99" * 32
    monitor, history = open_monitor(tmp_path, rpc)
    with pytest.raises(WatchError, match="different transaction"):
        monitor.transaction(DEMO_TX)
    assert history.records() == []
    history.close()
