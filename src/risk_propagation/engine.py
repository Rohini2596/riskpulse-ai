from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass(frozen=True)
class RiskSignal:
    event: str
    sentiment: float
    impact: float
    confidence: float


@dataclass(frozen=True)
class PropagatedScenario:
    event: str
    risk_factors: dict[str, float]
    scale: float
    action: str


class RiskPropagationEngine:
    def __init__(self, rules_path: str | Path):
        with Path(rules_path).open(encoding="utf-8") as file:
            self.rules = yaml.safe_load(file) or {}

    @staticmethod
    def action_for(signal: RiskSignal) -> str:
        if signal.impact >= 7 and signal.confidence >= 0.7:
            return "STRESS"
        if signal.impact >= 7:
            return "VERIFY"
        return "MONITOR"

    def propagate(self, signal: RiskSignal) -> PropagatedScenario:
        if not -1 <= signal.sentiment <= 1:
            raise ValueError("sentiment must be between -1 and 1")
        if not 1 <= signal.impact <= 10:
            raise ValueError("impact must be between 1 and 10")
        if not 0 <= signal.confidence <= 1:
            raise ValueError("confidence must be between 0 and 1")

        try:
            base_factors = self.rules[signal.event]["risk_factors"]
        except (KeyError, TypeError) as error:
            raise ValueError(
                f"No scenario rules configured for event: {signal.event}"
            ) from error

        impact_scale = 0.2 + 0.8 * ((signal.impact - 1) / 9)
        confidence_scale = 0.5 + 0.5 * signal.confidence
        sentiment_scale = max(0.5, min(1.5, 1.0 - 0.35 * signal.sentiment))
        total_scale = impact_scale * confidence_scale * sentiment_scale

        scaled_factors = {
            name: float(value) * total_scale * total_scale
            for name, value in base_factors.items()
        }

        return PropagatedScenario(
            event=signal.event,
            risk_factors=scaled_factors,
            scale=total_scale,
            action=self.action_for(signal),
        )