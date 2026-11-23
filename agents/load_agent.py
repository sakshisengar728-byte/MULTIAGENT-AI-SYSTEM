from base_agent import BaseAgent
from config import ESSENTIAL_LOAD_KW, PEAK_PRICE


class LoadAgent(BaseAgent):
    name = "load"

    def evaluate(self, t):
        load = t["load_kw"]
        essential = min(load, ESSENTIAL_LOAD_KW)
        flexible = round(max(0.0, load - essential), 2)
        if t["price_per_kwh"] >= PEAK_PRICE and flexible > 0.3:
            action = "SHED_FLEXIBLE_LOAD"
            reason = f"Peak tariff Rs. {t['price_per_kwh']}/kWh. Shedding {flexible} kW of flexible load."
        else:
            action = "MAINTAIN_NORMAL_LOAD"
            reason = "Tariff is normal or flexible load is small. All loads can run."
        return {
            "essential_load_kw": essential,
            "flexible_load_kw": flexible,
            "recommended_action": action,
            "reason": reason,
        }


if __name__ == "__main__":
    LoadAgent().run()
    