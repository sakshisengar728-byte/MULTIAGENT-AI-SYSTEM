from agents.base_agent import BaseAgent


class GenerationAgent(BaseAgent):
    name = "generation"

    def evaluate(self, t):
        solar, load = t["solar_kw"], t["load_kw"]
        surplus = round(solar - load, 2)
        if solar == 0:
            status, action, spare = "ZERO_GENERATION", "STANDBY", 0.0
            reason = "No solar output at this hour."
        elif surplus > 0:
            status, action, spare = "SURPLUS_GENERATION", "SUPPLY_LOAD_AND_STORE_SURPLUS", surplus
            reason = f"Solar {solar} kW exceeds load {load} kW. Surplus {surplus} kW can be stored."
        else:
            status, action, spare = "PARTIAL_GENERATION", "OFFSET_PORTION_OF_LOAD", 0.0
            reason = f"Solar {solar} kW covers part of the {load} kW load."
        return {
            "generation_status": status,
            "solar_kw": solar,
            "available_surplus_kw": spare,
            "recommended_action": action,
            "reason": reason,
        }


if __name__ == "__main__":
    GenerationAgent().run()