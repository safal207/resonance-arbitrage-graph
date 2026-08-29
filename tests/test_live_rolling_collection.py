from resonance_arbitrage_graph.live_scan import _collect_rolling_quotes
from resonance_arbitrage_graph.quotes import QuoteSnapshot
from resonance_arbitrage_graph.rolling_state import RollingMarketWindow, RollingWindowPolicy
from resonance_arbitrage_graph.window_regime import market_key


class FakeBinance:
    venue = "BINANCE_SPOT"

    def __init__(self):
        self.ts = 0

    def fetch(self, symbol: str, *, base_asset: str, quote_asset: str) -> QuoteSnapshot:
        self.ts += 1_000
        mid = 100.0 + self.ts / 100_000.0
        return QuoteSnapshot(
            venue=self.venue,
            symbol=symbol,
            base_asset=base_asset,
            quote_asset=quote_asset,
            bid_price=mid - 0.01,
            bid_qty=10.0,
            ask_price=mid + 0.01,
            ask_qty=10.0,
            observed_at_ms=self.ts,
            source_url=f"fixture:{symbol}",
        )


class JitteredBinance:
    venue = "BINANCE_SPOT"

    def __init__(self):
        self._timestamps = iter((1_000, 2_210, 3_520, 4_760, 6_100, 7_430))

    def fetch(self, symbol: str, *, base_asset: str, quote_asset: str) -> QuoteSnapshot:
        ts = next(self._timestamps)
        return QuoteSnapshot(
            venue=self.venue,
            symbol=symbol,
            base_asset=base_asset,
            quote_asset=quote_asset,
            bid_price=100.0,
            bid_qty=10.0,
            ask_price=100.1,
            ask_qty=10.0,
            observed_at_ms=ts,
            source_url=f"fixture:{symbol}",
        )


def test_live_collection_keeps_final_quote_as_window_tail():
    sleeps = []
    adapter = FakeBinance()
    pairs = [("BTCUSDT", "BTC", "USDT")]

    latest, history = _collect_rolling_quotes(
        adapter,
        pairs,
        sample_count=5,
        interval_ms=1_000,
        sleep_fn=sleeps.append,
    )

    key = market_key(adapter.venue, "BTCUSDT")
    assert len(history[key]) == 5
    assert history[key][-1] == latest[0]
    assert sleeps == [1.0, 1.0, 1.0, 1.0]

    window = RollingMarketWindow.from_quotes(
        history[key],
        policy=RollingWindowPolicy(horizon_ms=5_000, min_samples=5, min_coverage_ratio=0.8),
        end_ms=history[key][-1].observed_at_ms,
    )
    assert window.samples[-1].observed_at_ms == latest[0].observed_at_ms
    assert window.summary().complete is True


def test_campaign_002_window_is_complete_under_public_http_jitter():
    adapter = JitteredBinance()
    pairs = [("BTCUSDT", "BTC", "USDT")]

    latest, history = _collect_rolling_quotes(
        adapter,
        pairs,
        sample_count=6,
        interval_ms=1_000,
        sleep_fn=lambda _seconds: None,
    )

    key = market_key(adapter.venue, "BTCUSDT")
    window = RollingMarketWindow.from_quotes(
        history[key],
        policy=RollingWindowPolicy(
            horizon_ms=10_000,
            min_samples=6,
            min_coverage_ratio=0.5,
        ),
        end_ms=latest[0].observed_at_ms,
    )

    assert len(window.samples) == 6
    assert window.summary().complete is True
    assert window.summary().coverage_ratio > 0.6


def test_live_collection_rejects_too_few_samples_or_zero_interval():
    adapter = FakeBinance()
    pairs = [("BTCUSDT", "BTC", "USDT")]

    try:
        _collect_rolling_quotes(adapter, pairs, sample_count=2, interval_ms=1_000, sleep_fn=lambda _: None)
    except ValueError as exc:
        assert "sample count" in str(exc)
    else:
        raise AssertionError("expected sample-count validation")

    try:
        _collect_rolling_quotes(adapter, pairs, sample_count=3, interval_ms=0, sleep_fn=lambda _: None)
    except ValueError as exc:
        assert "interval" in str(exc)
    else:
        raise AssertionError("expected interval validation")
