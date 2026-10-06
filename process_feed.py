import json
from pathlib import Path

from src.ingestion.loader import load_all_sources
from src.nlp.engine import RiskNlpEngine
from src.risk_propagation.engine import (
    RiskPropagationEngine,
    RiskSignal as PropagationSignal,
)
from src.stress_testing.engine import StressTestEngine


PROJECT_FOLDER = Path(__file__).resolve().parent


def main():
    source_files = {
        "news": PROJECT_FOLDER / "data" / "news_sample.csv",
        "social": PROJECT_FOLDER / "data" / "social_sample.csv",
    }

    records = load_all_sources(source_files)
    nlp_engine = RiskNlpEngine()
    propagation_engine = RiskPropagationEngine(
        PROJECT_FOLDER / "data" / "scenario_rules.yaml"
    )
    stress_engine = StressTestEngine()
    portfolio = stress_engine.load_portfolio(
        PROJECT_FOLDER / "data" / "portfolio.csv"
    )

    results = []

    for record in records:
        nlp_signal = nlp_engine.analyze(
            record["text"],
            source=record["source"],
        )

        propagation_signal = PropagationSignal(
            event=nlp_signal.event,
            sentiment=nlp_signal.sentiment,
            impact=nlp_signal.impact,
            confidence=nlp_signal.confidence,
        )
        scenario = propagation_engine.propagate(propagation_signal)

        stress_result = None
        if scenario.action == "STRESS":
            stress_result = stress_engine.run(portfolio, scenario).to_dict()

        results.append({
            "record_id": record["record_id"],
            "risk_signal": nlp_signal.to_dict(),
            "action": scenario.action,
            "risk_factors": scenario.risk_factors,
            "stress_result": stress_result,
        })

    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()