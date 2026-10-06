import json
from pathlib import Path

from src.nlp.engine import RiskNlpEngine
from src.risk_propagation.engine import (
    RiskPropagationEngine,
    RiskSignal as PropagationSignal,
)
from src.stress_testing.engine import StressTestEngine


PROJECT_FOLDER = Path(__file__).resolve().parent


def main():
    # Demo event text; later this will come from news and social ingestion.
    text = (
        "TSMC faces major export restrictions as geopolitical tensions "
        "rise, raising concern for semiconductor supply chains."
    )

    # Step 1: Text -> entity, sentiment, event, confidence, impact.
    nlp_engine = RiskNlpEngine()
    nlp_signal = nlp_engine.analyze(text, source="demo-news")

    # Step 2: Convert the NLP output into the propagation engine's input type.
    propagation_signal = PropagationSignal(
        event=nlp_signal.event,
        sentiment=nlp_signal.sentiment,
        impact=nlp_signal.impact,
        confidence=nlp_signal.confidence,
    )

    # Step 3: Event -> portfolio risk factors.
    propagation_engine = RiskPropagationEngine(
        PROJECT_FOLDER / "data" / "scenario_rules.yaml"
    )
    scenario = propagation_engine.propagate(propagation_signal)

    # Step 4: Risk factors -> portfolio stress result.
    stress_engine = StressTestEngine()
    portfolio = stress_engine.load_portfolio(
        PROJECT_FOLDER / "data" / "portfolio.csv"
    )
    result = stress_engine.run(portfolio, scenario)

    output = {
        "risk_signal": nlp_signal.to_dict(),
        "risk_factors": scenario.risk_factors,
        "action": scenario.action,
        "stress_result": result.to_dict(),
    }
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()