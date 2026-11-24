"""Physical battery power limits for a one-hour simulation."""

from decimal import Decimal, ROUND_DOWN
from config import (
    BATTERY_CAPACITY_KWH,
    CHARGE_EFFICIENCY,
    MAX_BATTERY_KW,
    MAX_SOC,
    MIN_SOC,
)


def safe_round(value):
    """Round down to avoid exceeding physical limits."""
    return float(
        value.quantize(
            Decimal("0.01"),
            rounding=ROUND_DOWN
        )
    )


def battery_power_limits(soc):
    """Return safe charging and discharging power in kW."""

    soc = Decimal(str(soc))
    capacity = Decimal(str(BATTERY_CAPACITY_KWH))
    efficiency = Decimal(str(CHARGE_EFFICIENCY))
    max_power = Decimal(str(MAX_BATTERY_KW))
    duration = Decimal("1.0")

    remaining_capacity = max(
        Decimal("0"),
        capacity * (Decimal(str(MAX_SOC)) - soc) / 100
    )

    available_energy = max(
        Decimal("0"),
        capacity * (soc - Decimal(str(MIN_SOC))) / 100
    )

    charge_limit = min(
        max_power,
        remaining_capacity / (efficiency * duration)
    )

    discharge_limit = min(
        max_power,
        available_energy / duration
    )

    return {
        "max_charge_kw": safe_round(charge_limit),
        "max_discharge_kw": safe_round(discharge_limit),
    }
