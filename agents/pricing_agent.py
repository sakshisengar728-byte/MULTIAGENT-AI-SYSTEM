from base_agent import BaseAgent
from config import PEAK_PRICE


class PricingAgent(BaseAgent):
    name = "pricing"

    def evaluate(self, t):
        price = t["price_per_kwh"]
        if price >= PEAK_PRICE:
            tier, strategy = "PEAK", "MINIMIZE_GRID_IMPORT"
            reason = f"Peak tariff Rs. {price}/kWh. Minimise grid purchases."
        elif t["hour"] <= 5:
            tier, strategy = "OFF_PEAK_NIGHT", "ALLOW_GRID_OR_PRE_CHARGE"
            reason = f"Off-peak night tariff Rs. {price}/kWh. Grid power is economical."
        else:
            tier, strategy = "STANDARD_DAY", "MAXIMIZE_SOLAR_SELF_CONSUMPTION"
            reason = f"Standard tariff Rs. {price}/kWh. Use solar first."
        return {
            "tariff_tier": tier,
            "recommended_strategy": strategy,
            "reason": reason,
        }


if __name__ == "__main__":
    PricingAgent().run()