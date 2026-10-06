import csv
from dataclasses import asdict, dataclass
from pathlib import Path

from src.risk_propagation.engine import PropagatedScenario


@dataclass(frozen=True)
class AssetResult:
    asset_id: str
    asset_name: str
    asset_type: str
    before_usd: float
    pnl_usd: float
    after_usd: float


@dataclass(frozen=True)
class StressResult:
    event: str
    action: str
    before_usd: float
    after_usd: float
    pnl_usd: float
    loss_pct: float
    by_asset_type: dict[str, float]
    assets: list[AssetResult]

    def to_dict(self):
        return asdict(self)


class StressTestEngine:
    def load_portfolio(self, path: str | Path) -> list[dict[str, str]]:
        with Path(path).open(newline="", encoding="utf-8-sig") as file:
            return list(csv.DictReader(file))

    @staticmethod
    def asset_pnl(
        asset: dict[str, str],
        shocks: dict[str, float],
    ) -> float:
        asset_type = asset["asset_type"]
        market_value = float(asset["market_value_usd"])

        if asset_type == "equity":
            beta = float(asset["beta"] or 1)
            return market_value * shocks["equity_shock"] * beta

        if asset_type == "energy_equity":
            beta = float(asset["beta"] or 1)
            return market_value * shocks["energy_equity_shock"] * beta

        if asset_type == "bond":
            rate_change = shocks["government_rate_change_bps"] / 10_000
            spread_change = shocks["corporate_spread_bps"] / 10_000
            duration = float(asset["duration_years"])
            spread_duration = float(asset["spread_duration_years"])
            price_change = (
                -duration * rate_change
                - spread_duration * spread_change
            )
            return market_value * price_change

        if asset_type == "government_bond":
            rate_change = shocks["government_rate_change_bps"] / 10_000
            duration = float(asset["duration_years"])
            return market_value * (-duration * rate_change)

        if asset_type == "loan":
            spread_change = shocks["loan_spread_bps"] / 10_000
            spread_duration = float(asset["spread_duration_years"])
            return market_value * (-spread_duration * spread_change)

        if asset_type == "derivative":
            notional = float(asset["notional_usd"])
            delta = float(asset["delta"])
            return notional * delta * shocks["equity_shock"]

        raise ValueError(f"Unsupported asset_type: {asset_type}")

    def run(
        self,
        portfolio: list[dict[str, str]],
        scenario: PropagatedScenario,
    ) -> StressResult:
        assets = []
        attribution = {}

        for row in portfolio:
            before = float(row["market_value_usd"])
            pnl = self.asset_pnl(row, scenario.risk_factors)
            assets.append(
                AssetResult(
                    asset_id=row["asset_id"],
                    asset_name=row["asset_name"],
                    asset_type=row["asset_type"],
                    before_usd=before,
                    pnl_usd=pnl,
                    after_usd=before + pnl,
                )
            )
            kind = row["asset_type"]
            attribution[kind] = attribution.get(kind, 0.0) + pnl

        before_total = sum(asset.before_usd for asset in assets)
        pnl_total = sum(asset.pnl_usd for asset in assets)
        after_total = before_total + pnl_total
        pnl_percent = pnl_total / before_total * 100 if before_total else 0

        return StressResult(
            event=scenario.event,
            action=scenario.action,
            before_usd=before_total,
            after_usd=after_total,
            pnl_usd=pnl_total,
            loss_pct=pnl_percent,
            by_asset_type=attribution,
            assets=assets,
        )