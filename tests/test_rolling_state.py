from dataclasses import replace

import pytest

from resonance_arbitrage_graph.quotes import QuoteSnapshot
from resonance_arbitrage_graph.rolling_state import (
    RollingMarketWindow,
    RollingWindowPolicy,
)


def _quote(ts: int, mid: float, *, spread: float = 0.1) -> QuoteSnapshot:
    return QuoteSnapshot(
        venue="binance",
        symbol="BTCUSDT",
        base_asset="BTC",
        quote_asset="USDT",
        bid_price=mid - spread / 2,
        bid_qty=5.0,
        ask_price=mid + spread / 2,
        ask_qty=4.0,
        observed_at_ms=ts,
        source_url="fixture:BTCUSDT",
    )


def _window() -> RollingMarketWindow:
    quotes = [
        _quote(0, 100.0),
        _quote(15_000, 100.2),
        _quote(30_000, 99.8),
        _quote(45_000, 100.4),
        _quote(60_000, 100.1),
    ]
    return RollingMarketWindow.from_quotes(
        quotes,
        policy=RollingWindowPolicy(
            horizon_ms=60_000,
            min_samples=5,
            min_coverage_ratio=1.0,
        ),
        end_ms=60_000,
    )


def test_same_ordered_samples_produce_same_digest_and_volatility():
    first = _window()
    second = _window()

    assert first.sha256 == second.sha256
    assert first.canonical_json() == second.canonical_json()
    assert first.summary().complete is True
    assert first.summary().short_window_return_volatility_bps == pytest.approx(
        second.summary().short_window_return_volatility_bps
    )
    assert first.summary().short_window_return_volatility_bps > 0.0


def test_duplicate_or_reordered_timestamps_are_rejected():
    with pytest.raises(ValueError, match="strictly timestamp ordered"):
        RollingMarketWindow.from_quotes(
            [_quote(1_000, 100.0), _quote(1_000, 100.1)],
            policy=RollingWindowPolicy(horizon_ms=1_000, min_samples=2),
            end_ms=1_000,
        )

    with pytest.raises(ValueError, match="strictly timestamp ordered"):
        RollingMarketWindow.from_quotes(
            [_quote(2_000, 100.0), _quote(1_000, 100.1)],
            policy=RollingWindowPolicy(horizon_ms=2_000, min_samples=2),
            end_ms=2_000,
        )


def test_window_digest_changes_when_sample_or_provenance_is_tampered():
    original = _window()
    samples = list(original.samples)
    samples[2] = replace(samples[2], bid_price=samples[2].bid_price + 0.01)
    tampered_price = RollingMarketWindow(policy=original.policy, samples=tuple(samples))

    provenance_samples = list(original.samples)
    provenance_samples[2] = replace(provenance_samples[2], source_url="fixture:other")
    tampered_provenance = RollingMarketWindow(
        policy=original.policy,
        samples=tuple(provenance_samples),
    )

    assert original.sha256 != tampered_price.sha256
    assert original.sha256 != tampered_provenance.sha256


def test_sample_timestamp_provenance_cannot_drift():
    sample = _window().samples[0]

    with pytest.raises(ValueError, match="freshness_reference_ms"):
        replace(sample, freshness_reference_ms=sample.freshness_reference_ms + 1)

    with pytest.raises(ValueError, match="exchange_published"):
        replace(sample, timestamp_class="exchange_published")


def test_insufficient_samples_or_coverage_fail_closed_in_summary():
    window = RollingMarketWindow.from_quotes(
        [_quote(50_000, 100.0), _quote(60_000, 100.1)],
        policy=RollingWindowPolicy(
            horizon_ms=60_000,
            min_samples=5,
            min_coverage_ratio=0.8,
        ),
        end_ms=60_000,
    )
    summary = window.summary()

    assert summary.complete is False
    assert "insufficient_sample_count" in summary.reasons
    assert "insufficient_time_coverage" in summary.reasons


def test_samples_from_different_markets_are_rejected():
    other = QuoteSnapshot(
        venue="binance",
        symbol="ETHUSDT",
        base_asset="ETH",
        quote_asset="USDT",
        bid_price=50.0,
        bid_qty=5.0,
        ask_price=50.1,
        ask_qty=4.0,
        observed_at_ms=15_000,
        source_url="fixture:ETHUSDT",
    )
    with pytest.raises(ValueError, match="one exact market"):
        RollingMarketWindow.from_quotes(
            [_quote(0, 100.0), other],
            policy=RollingWindowPolicy(horizon_ms=60_000, min_samples=2),
            end_ms=60_000,
        )
