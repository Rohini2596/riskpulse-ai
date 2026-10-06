import json
from pathlib import Path

from src.risk_propagation.engine import RiskPropagationEngine, RiskSignal
from src.stress_testing.engine import StressTestEngine


PROJECT_FOLDER = Path(__file__).resolve().parent


def main():
    signal = RiskSignal(
        event="Geopolitical",
        sentiment=-0.75,
        impact=8.5,
        confidence=0.82,
    )

    propagation_engine = RiskPropagationEngine(
        PROJECT_FOLDER / "data" / "scenario_rules.yaml"
    )
    scenario = propagation_engine.propagate(signal)

    stress_engine = StressTestEngine()
    portfolio = stress_engine.load_portfolio(
        PROJECT_FOLDER / "data" / "portfolio.csv"
    )
    result = stress_engine.run(portfolio, scenario)

    output = {
        "signal": {
            "event": signal.event,
            "sentiment": signal.sentiment,
            "impact": signal.impact,
            "confidence": signal.confidence,
        },
        "scenario": {
            "event": scenario.event,
            "action": scenario.action,
            "scale": scenario.scale,
            "risk_factors": scenario.risk_factors,
        },
        "stress_result": result.to_dict(),
    }

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()