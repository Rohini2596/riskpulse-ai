import unittest
from pathlib import Path

from src.risk_propagation.engine import PropagatedScenario
from src.stress_testing.engine import StressTestEngine


PROJECT_FOLDER = Path(__file__).resolve().parents[1]
PORTFOLIO_PATH = PROJECT_FOLDER / "data" / "portfolio.csv"


class StressTestTests(unittest.TestCase):
    def setUp(self):
        self.engine = StressTestEngine()
        self.portfolio = self.engine.load_portfolio(PORTFOLIO_PATH)

    def test_portfolio_cash_value_is_90_million(self):
        cash_value = sum(
            float(asset["market_value_usd"])
            for asset in self.portfolio
        )

        self.assertEqual(cash_value, 90_000_000)

    def test_negative_equity_shock_causes_equity_loss(self):
        scenario = PropagatedScenario(
            event="Test",
            risk_factors={
                "equity_shock": -0.10,
                "energy_equity_shock": -0.10,
                "government_rate_change_bps": 0,
                "corporate_spread_bps": 0,
                "loan_spread_bps": 0,
            },
            scale=1.0,
            action="STRESS",
        )

        result = self.engine.run(self.portfolio, scenario)

        equity = next(
            asset for asset in result.assets
            if asset.asset_type == "equity"
        )
        self.assertLess(equity.pnl_usd, 0)

    def test_after_value_equals_before_plus_pnl(self):
        scenario = PropagatedScenario(
            event="Test",
            risk_factors={
                "equity_shock": -0.05,
                "energy_equity_shock": -0.02,
                "government_rate_change_bps": 25,
                "corporate_spread_bps": 50,
                "loan_spread_bps": 30,
            },
            scale=1.0,
            action="STRESS",
        )

        result = self.engine.run(self.portfolio, scenario)

        self.assertAlmostEqual(
            result.after_usd,
            result.before_usd + result.pnl_usd,
        )


if __name__ == "__main__":
    unittest.main()