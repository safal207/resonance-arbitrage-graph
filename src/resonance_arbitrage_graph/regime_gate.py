from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json

from .model import Verdict
from .regime import MarketRegime


class RegimeAction(str, Enum):
    ALLOW = "ALLOW"
    OBSERVE_ONLY = "OBSERVE_ONLY"
    REJECT = "REJECT"


@dataclass(frozen=True, slots=True)
class RegimeExecutionPolicy:
    normal: RegimeAction = RegimeAction.ALLOW
    volatile: RegimeAction = RegimeAction.OBSERVE_ONLY
    thin_liquidity: RegimeAction = RegimeAction.OBSERVE_ONLY
    dislocated: RegimeAction = RegimeAction.OBSERVE_ONLY
    unknown: RegimeAction = RegimeAction.REJECT

    def __post_init__(self) -> None:
        for name in (
            "normal",
            "volatile",
            "thin_liquidity",
            "dislocated",
            "unknown",
        ):
            try:
                value = RegimeAction(getattr(self, name))
            except (TypeError, ValueError) as exc:
                raise ValueError(f"{name} must be a RegimeAction") from exc
            object.__setattr__(self, name, value)
        if self.unknown is not RegimeAction.REJECT:
            raise ValueError("UNKNOWN market regime must remain fail-closed to REJECT")

    def action_for(self, regime: MarketRegime) -> RegimeAction:
        if not isinstance(regime, MarketRegime):
            raise ValueError("regime must be MarketRegime")
        return {
            MarketRegime.NORMAL: self.normal,
            MarketRegime.VOLATILE: self.volatile,
            MarketRegime.THIN_LIQUIDITY: self.thin_liquidity,
            MarketRegime.DISLOCATED: self.dislocated,
            MarketRegime.UNKNOWN: self.unknown,
        }[regime]

    def canonical_payload(self) -> dict[str, str]:
        return {
            "schema": "resonance.arbitrage.regime-execution-policy/v0.1",
            "normal": self.normal.value,
            "volatile": self.volatile.value,
            "thin_liquidity": self.thin_liquidity.value,
            "dislocated": self.dislocated.value,
            "unknown": self.unknown.value,
        }

    @property
    def sha256(self) -> str:
        raw = json.dumps(
            self.canonical_payload(),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
        return hashlib.sha256(raw).hexdigest()


@dataclass(frozen=True, slots=True)
class RegimeGateResult:
    base_verdict: Verdict
    final_verdict: Verdict
    regime: MarketRegime
    action: RegimeAction
    policy_sha256: str
    reasons: tuple[str, ...]

    def to_payload(self) -> dict[str, object]:
        return {
            "schema": "resonance.arbitrage.regime-gate-result/v0.1",
            "base_verdict": self.base_verdict.value,
            "market_regime": self.regime.value,
            "action": self.action.value,
            "final_verdict": self.final_verdict.value,
            "policy_sha256": self.policy_sha256,
            "reasons": list(self.reasons),
        }


_VERDICT_LEVEL = {
    Verdict.REJECT: 0,
    Verdict.OBSERVE: 1,
    Verdict.EXECUTE_SIM: 2,
}


def apply_regime_gate(
    base_verdict: Verdict,
    regime: MarketRegime,
    *,
    policy: RegimeExecutionPolicy | None = None,
) -> RegimeGateResult:
    if not isinstance(base_verdict, Verdict):
        raise ValueError("base_verdict must be Verdict")
    if not isinstance(regime, MarketRegime):
        raise ValueError("regime must be MarketRegime")

    active = policy or RegimeExecutionPolicy()
    action = active.action_for(regime)

    if base_verdict is Verdict.REJECT or action is RegimeAction.REJECT:
        final_verdict = Verdict.REJECT
    elif base_verdict is Verdict.OBSERVE or action is RegimeAction.OBSERVE_ONLY:
        final_verdict = Verdict.OBSERVE
    else:
        final_verdict = Verdict.EXECUTE_SIM

    if _VERDICT_LEVEL[final_verdict] > _VERDICT_LEVEL[base_verdict]:
        raise RuntimeError("regime gate attempted to upgrade verifier verdict")

    reasons = (
        f"BASE_VERDICT:{base_verdict.value}",
        f"MARKET_REGIME:{regime.value}",
        f"REGIME_ACTION:{action.value}",
        f"FINAL_VERDICT:{final_verdict.value}",
    )
    return RegimeGateResult(
        base_verdict=base_verdict,
        final_verdict=final_verdict,
        regime=regime,
        action=action,
        policy_sha256=active.sha256,
        reasons=reasons,
    )
