import random
import threading
import uuid
from datetime import datetime

from config import (BATTERY_CAPACITY_KWH, CHARGE_EFFICIENCY, MAX_SOC, MIN_SOC,
                    OFFPEAK_PRICE, PEAK_PRICE)


class EnergySimulator:
    """Simulates one hour of a home microgrid each time step() is called."""

    def __init__(self, initial_soc=70.0):
        self.hour = 0
        self.step_id = 0
        self.session_id = uuid.uuid4().hex
        self.soc = initial_soc
        self.lock = threading.Lock()

    def step(self):
        with self.lock:
            load = round(random.uniform(1.5, 3.5), 2)
            sunlight = max(0.0, 1.0 - abs(self.hour - 12) / 6.0)   # 1.0 at noon, 0 at 06:00 and 18:00
            solar = round(5.0 * sunlight, 2)
            price = PEAK_PRICE if 17 <= self.hour <= 21 else OFFPEAK_PRICE

            reading = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "hour": self.hour,
                "step_id": f"{self.session_id}:{self.step_id}",
                "load_kw": load,
                "solar_kw": solar,
                "battery_soc": round(self.soc, 1),
                "battery_soc_exact": self.soc,
                "battery_energy_kwh": round(BATTERY_CAPACITY_KWH * self.soc / 100, 2),
                "grid_kw": round(max(0.0, load - solar), 2),
                "price_per_kwh": price,
                "currency": "INR",
            }
            self.hour = (self.hour + 1) % 24
            self.step_id += 1
            return reading

    def apply_dispatch(self, decision):
        """Closed loop: the battery level follows the coordinator's decision."""
        with self.lock:
            charged_kwh = decision["solar_to_battery_kw"] * CHARGE_EFFICIENCY   # one hour per step
            discharged_kwh = decision["battery_to_load_kw"]
            self.soc += (charged_kwh - discharged_kwh) / BATTERY_CAPACITY_KWH * 100
            self.soc = min(MAX_SOC, max(MIN_SOC, self.soc))