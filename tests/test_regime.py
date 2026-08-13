import pytest

from resonance_arbitrage_graph.regime import (
    MarketRegime,
    RegimeFeatures,
    RegimePolicy,
    classify_market_regime,
    merge_regime_context,
)


def _features(**overrides):
    data = {
        "normalized_spread_bps": 5.0,
        "top_of_book_capacity_ratio": 4.0,
        "quote_age_ms": 100,
        "quote_age_dispersion_ms": 25,
        "cross_rate_dislocation_bps": 5.0,
        "short_window_return_volatility_bps": 20.0,
    }
    data.update(overrides)
    return RegimeFeatures(**data)


def test_normal_regime_is_deterministic():
    features = _features()
    first = classify_market_regime(features)
    second = classify_market_regime(features)
    assert first == second
    assert first.regime is MarketRegime.NORMAL


def test_stale_or_time_incoherent_features_fail_closed_unknown():
    stale = classify_market_regime(_features(quote_age_ms=3_001))
    incoherent = classify_market_regime(_features(quote_age_dispersion_ms=1_501))
    assert stale.regime is MarketRegime.UNKNOWN
    assert incoherent.regime is MarketRegime.UNKNOWN


def test_dislocation_has_precedence_over_volatility_and_thin_liquidity():
    result = classify_market_regime(
        _features(
            cross_rate_dislocation_bps=50.0,
            short_window_return_volatility_bps=100.0,
            top_of_book_capacity_ratio=1.0,
        )
    )
    assert result.regime is MarketRegime.DISLOCATED
    assert result.reasons == ("cross_rate_dislocation",)


def test_thin_liquidity_has_precedence_over_volatility():
    result = classify_market_regime(
        _features(
            cross_rate_dislocation_bps=10.0,
            top_of_book_capacity_ratio=1.0,
            short_window_return_volatility_bps=100.0,
        )
    )
    assert result.regime is MarketRegime.THIN_LIQUIDITY
    assert "low_capacity_ratio" in result.reasons


def test_wide_spread_is_thin_liquidity_signal():
    result = classify_market_regime(_features(normalized_spread_bps=25.0))
    assert result.regime is MarketRegime.THIN_LIQUIDITY
    assert "wide_spread" in result.reasons


def test_volatility_boundary_is_inclusive():
    result = classify_market_regime(
        _features(short_window_return_volatility_bps=75.0)
    )
    assert result.regime is MarketRegime.VOLATILE


def test_policy_and_feature_inputs_fail_closed_on_invalid_numbers():
    with pytest.raises(ValueError):
        RegimePolicy(volatile_return_bps=float("nan"))
    with pytest.raises(ValueError):
        RegimeFeatures(
            normalized_spread_bps=1.0,
            top_of_book_capacity_ratio=0.0,
            quote_age_ms=1,
            quote_age_dispersion_ms=1,
        )


def test_classification_market_context_is_strict_and_explicit():
    result = classify_market_regime(_features())
    context = result.to_market_context()
    assert context["regime"] == "NORMAL"
    assert context["regime_features"]["normalized_spread_bps"] == 5.0
    assert context["regime_reasons"] == ["within_normal_thresholds"]


def test_merge_regime_context_preserves_base_and_rejects_override():
    result = classify_market_regime(_features())
    merged = merge_regime_context({"venue": "binance"}, result)
    assert merged["venue"] == "binance"
    assert merged["regime"] == "NORMAL"

    with pytest.raises(ValueError, match="conflicts"):
        merge_regime_context({"venue": "binance", "regime": "VOLATILE"}, result)
