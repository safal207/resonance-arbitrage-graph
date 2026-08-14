import pytest

from resonance_arbitrage_graph.engine import Policy
from resonance_arbitrage_graph.predictive import (
    HistoricalMeanBaseline,
    build_predictive_dataset,
    build_predictive_row,
    chronological_predictive_split,
    evaluate_shadow_predictions,
)
from resonance_arbitrage_graph.quotes import CostAssumption, QuoteSnapshot
from resonance_arbitrage_graph.regime import RegimePolicy
from resonance_arbitrage_graph.replay import (
    ReplayBundle,
    ReplayCase,
    ReplayLeg,
    ReplayOutcome,
    ReplaySide,
)
from resonance_arbitrage_graph.rolling_state import RollingMarketWindow, RollingWindowPolicy
from resonance_arbitrage_graph.window_regime import market_key


ZERO = CostAssumption(fee_bps=0.0, slippage_bps=0.0)
WINDOW_POLICY = RollingWindowPolicy(horizon_ms=60_000, min_samples=5, min_coverage_ratio=1.0)


def _quote(symbol: str, base: str, quote: str, ts: int, mid: float, spread: float) -> QuoteSnapshot:
    return QuoteSnapshot(
        venue="fixture",
        symbol=symbol,
        base_asset=base,
        quote_asset=quote,
        bid_price=mid - spread / 2.0,
        bid_qty=1_000.0,
        ask_price=mid + spread / 2.0,
        ask_qty=1_000.0,
        observed_at_ms=ts,
        source_url=f"fixture:{symbol}:{ts}",
    )


def _market_series(
    symbol: str,
    base: str,
    quote: str,
    mids: list[float],
    spread: float,
    end_ms: int,
):
    times = (
        end_ms - 60_000,
        end_ms - 45_000,
        end_ms - 30_000,
        end_ms - 15_000,
        end_ms,
    )
    quotes = tuple(
        _quote(symbol, base, quote, ts, mid, spread)
        for ts, mid in zip(times, mids)
    )
    return quotes, RollingMarketWindow.from_quotes(
        quotes,
        policy=WINDOW_POLICY,
        end_ms=end_ms,
    )


def _decision_state(end_ms: int):
    btc_series, btc_window = _market_series(
        "BTCUSDT", "BTC", "USDT", [99.99, 100.00, 99.98, 100.01, 99.995], 0.01, end_ms
    )
    ethbtc_series, ethbtc_window = _market_series(
        "ETHBTC", "ETH", "BTC", [0.49994, 0.49996, 0.49993, 0.49997, 0.49995], 0.0001, end_ms
    )
    ethusdt_series, ethusdt_window = _market_series(
        "ETHUSDT", "ETH", "USDT", [50.17, 50.18, 50.16, 50.19, 50.185], 0.01, end_ms
    )
    snapshots = (btc_series[-1], ethbtc_series[-1], ethusdt_series[-1])
    windows = {
        market_key("fixture", "BTCUSDT"): btc_window,
        market_key("fixture", "ETHBTC"): ethbtc_window,
        market_key("fixture", "ETHUSDT"): ethusdt_window,
    }
    legs = (
        ReplayLeg(0, ReplaySide.BUY, ZERO),
        ReplayLeg(1, ReplaySide.BUY, ZERO),
        ReplayLeg(2, ReplaySide.SELL, ZERO),
    )
    return snapshots, windows, legs


def _case(
    operation: str,
    *,
    decision_ms: int,
    observed_at_ms: int,
    realized_edge_bps: float | None,
    expired: bool = False,
) -> ReplayCase:
    snapshots, windows, legs = _decision_state(decision_ms)
    return ReplayCase(
        case_id=f"{operation}-a1",
        logical_operation_id=operation,
        attempt=1,
        detected_at_ms=decision_ms,
        evaluation_time_ms=decision_ms,
        start_amount=1_000.0,
        snapshots=snapshots,
        windows_by_market=windows,
        legs=legs,
        engine_policy=Policy(),
        regime_policy=RegimePolicy(),
        outcome=ReplayOutcome(
            observed_at_ms=observed_at_ms,
            realized_net_edge_bps=realized_edge_bps,
            expired=expired,
        ),
    )


def test_predictive_row_uses_decision_time_features_and_later_targets():
    case = _case(
        "op-row",
        decision_ms=100_000,
        observed_at_ms=110_000,
        realized_edge_bps=40.0,
    )
    row = build_predictive_row(case)

    assert row.logical_operation_id == "op-row"
    assert row.decision_at_ms == 100_000
    assert row.features.route_hops == 3
    assert row.features.expected_edge_bps == pytest.approx(36.0, abs=0.05)
    assert row.regime == "NORMAL"
    assert row.targets.target_available_at_ms == 110_000
    assert row.targets.realized_net_edge_bps == 40.0
    assert row.targets.survived is True
    assert row.targets.positive_edge is True
    assert row.sha256 == build_predictive_row(case).sha256


def test_chronological_split_excludes_late_arriving_training_target():
    bundle = ReplayBundle(
        cases=(
            _case("op-1", decision_ms=100_000, observed_at_ms=120_000, realized_edge_bps=40.0),
            _case("op-2", decision_ms=200_000, observed_at_ms=350_000, realized_edge_bps=20.0),
            _case("op-3", decision_ms=300_000, observed_at_ms=310_000, realized_edge_bps=10.0),
        )
    )
    dataset = build_predictive_dataset(bundle)
    split = chronological_predictive_split(dataset, validation_fraction=1 / 3)

    assert [row.logical_operation_id for row in split.training_rows] == ["op-1"]
    assert [row.logical_operation_id for row in split.excluded_late_target_rows] == ["op-2"]
    assert [row.logical_operation_id for row in split.validation_rows] == ["op-3"]
    assert split.validation_start_ms == 300_000


def test_historical_baseline_and_shadow_pnl_are_deterministic():
    bundle = ReplayBundle(
        cases=(
            _case("op-1", decision_ms=100_000, observed_at_ms=110_000, realized_edge_bps=40.0),
            _case("op-2", decision_ms=200_000, observed_at_ms=210_000, realized_edge_bps=-10.0),
            _case("op-3", decision_ms=300_000, observed_at_ms=310_000, realized_edge_bps=20.0),
            _case(
                "op-4",
                decision_ms=400_000,
                observed_at_ms=410_000,
                realized_edge_bps=None,
                expired=True,
            ),
        )
    )
    dataset = build_predictive_dataset(bundle)
    split = chronological_predictive_split(dataset, validation_fraction=0.5)
    baseline = HistoricalMeanBaseline.fit(split.training_rows)
    predictions = baseline.predict(split.validation_rows)
    report = evaluate_shadow_predictions(split.validation_rows, predictions)

    assert baseline.mean_realized_edge_bps == pytest.approx(15.0)
    assert baseline.survival_probability == pytest.approx(1.0)
    assert baseline.positive_edge_probability == pytest.approx(0.5)
    assert report.evaluated_rows == 2
    assert report.selected_rows == 2
    assert report.selected_realized_rows == 1
    assert report.selected_expired_rows == 1
    assert report.selected_realized_pnl_units == pytest.approx(2.0)
