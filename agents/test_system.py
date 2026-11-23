from agents.generation_agent import GenerationAgent
from agents.load_agent import LoadAgent
from agents.pricing_agent import PricingAgent
from agents.storage_agent import StorageAgent
from coordinator import decide
from energy_simulator import EnergySimulator
from llm_explainer import template_explanation

AGENTS = [LoadAgent(), GenerationAgent(), StorageAgent(), PricingAgent()]


def run(telemetry):
    proposals = {a.name: a.evaluate(telemetry) for a in AGENTS}
    return decide(telemetry, proposals)


def test_scenario_a_noon_solar_surplus():
    d = run({"hour": 12, "load_kw": 2.2, "solar_kw": 4.8,
             "battery_soc": 55.0, "price_per_kwh": 4.0})
    assert d["solar_to_load_kw"] == 2.2
    assert d["solar_to_battery_kw"] == 2.5
    assert d["solar_exported_kw"] == 0.1      # 2.6 kW surplus minus 2.5 kW battery limit
    assert d["grid_import_kw"] == 0.0


def test_scenario_b_evening_peak_tariff():
    d = run({"hour": 18, "load_kw": 3.0, "solar_kw": 0.0,
             "battery_soc": 75.0, "price_per_kwh": 8.0})
    assert d["load_shed_kw"] == 1.8
    assert d["battery_to_load_kw"] == 1.2
    assert d["grid_import_kw"] == 0.0


def test_scenario_c_low_battery_guard():
    d = run({"hour": 20, "load_kw": 2.5, "solar_kw": 0.0,
             "battery_soc": 18.0, "price_per_kwh": 8.0})
    assert d["battery_to_load_kw"] == 0.0     # SOC at or below 20%: discharge blocked
    assert d["load_shed_kw"] == 1.3
    assert d["grid_import_kw"] == 1.2


def test_essential_load_is_never_shed():
    d = run({"hour": 19, "load_kw": 2.5, "solar_kw": 0.0,
             "battery_soc": 80.0, "price_per_kwh": 8.0})
    assert d["active_load_kw"] >= 1.2


def test_battery_soc_stays_within_limits():
    sim = EnergySimulator(initial_soc=89.0)
    sim.apply_dispatch({"solar_to_battery_kw": 2.5, "battery_to_load_kw": 0.0})
    assert sim.soc <= 90.0
    sim.soc = 21.0
    sim.apply_dispatch({"solar_to_battery_kw": 0.0, "battery_to_load_kw": 2.5})
    assert sim.soc >= 20.0


def test_llm_fallback_text_contains_numbers():
    text = template_explanation({"hour": 12, "solar_to_load_kw": 2.2, "battery_to_load_kw": 0.0,
                                 "grid_import_kw": 0.0, "load_shed_kw": 0.0})
    assert "2.2 kW" in text