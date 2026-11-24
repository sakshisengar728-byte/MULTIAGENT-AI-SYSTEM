"""Electricity cost and savings analysis for the microgrid."""

def calculate_cost(decision):
    duration = 1.0

    active_load = decision["active_load_kw"]
    shed_load = decision["load_shed_kw"]
    grid_import = decision["grid_import_kw"]
    tariff = decision["grid_price_per_kwh"]

    original_load = active_load + shed_load

    baseline_cost = original_load * duration * tariff
    served_load_cost = active_load * duration * tariff
    optimized_cost = grid_import * duration * tariff

    energy_savings = served_load_cost - optimized_cost
    shedding_savings = shed_load * duration * tariff
    total_savings = baseline_cost - optimized_cost

    savings_percent = (
        energy_savings / served_load_cost * 100
        if served_load_cost > 0 else 0.0
    )

    return {
        "hour": decision["hour"],
        "currency": "INR",
        "baseline_cost": round(baseline_cost, 2),
        "served_load_cost": round(served_load_cost, 2),
        "optimized_cost": round(optimized_cost, 2),
        "energy_savings": round(energy_savings, 2),
        "shedding_savings": round(shedding_savings, 2),
        "total_savings": round(total_savings, 2),
        "savings_percent": round(savings_percent, 2),
        "grid_energy_kwh": round(grid_import * duration, 2),
        "served_energy_kwh": round(active_load * duration, 2),
        "shed_energy_kwh": round(shed_load * duration, 2),
    }


def calculate_cumulative(history):
    """Summarize electricity costs for recent simulated hours."""

    records = history[-24:]

    keys = [
        "baseline_cost",
        "served_load_cost",
        "optimized_cost",
        "energy_savings",
        "shedding_savings",
        "total_savings",
        "grid_energy_kwh",
        "served_energy_kwh",
        "shed_energy_kwh",
    ]

    totals = {
        key: round(sum(r[key] for r in records), 2)
        for key in keys
    }

    served_cost = totals["served_load_cost"]

    totals["savings_percent"] = round(
        totals["energy_savings"] / served_cost * 100
        if served_cost > 0 else 0.0, 2
    )

    totals["hours_recorded"] = len(records)
    totals["currency"] = "INR"

    totals["complete_24_hours"] = (
        len(records) == 24
        and all(
            records[i]["hour"] ==
            (records[i - 1]["hour"] + 1) % 24
            for i in range(1, len(records))
        )
    )

    return totals
