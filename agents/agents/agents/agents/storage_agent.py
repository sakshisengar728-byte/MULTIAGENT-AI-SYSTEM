from agents.base_agent import BaseAgent
from config import MAX_BATTERY_KW, MAX_SOC, MIN_SOC, PEAK_PRICE


class StorageAgent(BaseAgent):
    name = "storage"

    def evaluate(self, t):
        soc = t["battery_soc"]
        surplus = round(t["solar_kw"] - t["load_kw"], 2)
        deficit = round(max(0.0, t["load_kw"] - t["solar_kw"]), 2)

        if surplus > 0 and soc < MAX_SOC:
            power = round(min(surplus, MAX_BATTERY_KW), 2)
            return {"recommended_action": "CHARGE", "recommended_power_kw": power,
                    "reason": f"Surplus solar available. Charging at {power} kW."}
        if surplus > 0:
            return {"recommended_action": "HOLD_FULL", "recommended_power_kw": 0.0,
                    "reason": f"Battery at {soc}% is at the {MAX_SOC}% ceiling. Charging blocked."}
        if t["price_per_kwh"] >= PEAK_PRICE and soc > MIN_SOC:
            power = round(min(deficit, MAX_BATTERY_KW), 2)
            return {"recommended_action": "DISCHARGE", "recommended_power_kw": power,
                    "reason": f"Peak tariff. Discharging up to {power} kW to avoid grid import."}
        if deficit > 0 and soc <= MIN_SOC:
            return {"recommended_action": "HOLD_EMPTY", "recommended_power_kw": 0.0,
                    "reason": f"Battery at {soc}% is at the {MIN_SOC}% reserve. Discharge blocked."}
        return {"recommended_action": "HOLD", "recommended_power_kw": 0.0,
                "reason": "Steady state. No charging or discharging needed."}


if __name__ == "__main__":
    StorageAgent().run()