import unittest
from pathlib import Path

from src.risk_propagation.engine import RiskPropagationEngine, RiskSignal


PROJECT_FOLDER = Path(__file__).resolve().parents[1]
RULES_PATH = PROJECT_FOLDER / "data" / "scenario_rules.yaml"


class RiskPropagationTests(unittest.TestCase):
    def setUp(self):
        self.engine = RiskPropagationEngine(RULES_PATH)

    def test_high_impact_and_confidence_triggers_stress(self):
        signal = RiskSignal(
            event="Geopolitical",
            sentiment=-0.5,
            impact=8,
            confidence=0.8,
        )

        scenario = self.engine.propagate(signal)

        self.assertEqual(scenario.action, "STRESS")

    def test_high_impact_low_confidence_triggers_verify(self):
        signal = RiskSignal(
            event="Geopolitical",
            sentiment=-0.5,
            impact=8,
            confidence=0.4,
        )

        scenario = self.engine.propagate(signal)

        self.assertEqual(scenario.action, "VERIFY")

    def test_low_impact_triggers_monitor(self):
        signal = RiskSignal(
            event="Geopolitical",
            sentiment=0.0,
            impact=4,
            confidence=0.9,
        )

        scenario = self.engine.propagate(signal)

        self.assertEqual(scenario.action, "MONITOR")

    def test_invalid_sentiment_is_rejected(self):
        signal = RiskSignal(
            event="Geopolitical",
            sentiment=-1.5,
            impact=8,
            confidence=0.8,
        )

        with self.assertRaises(ValueError):
            self.engine.propagate(signal)


if __name__ == "__main__":
    unittest.main()