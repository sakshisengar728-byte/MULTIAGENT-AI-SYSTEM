import json

import paho.mqtt.client as mqtt

from config import (BROKER_HOST, BROKER_PORT, DECISION_TOPIC, MAX_BATTERY_KW,
                    MAX_SOC, MIN_SOC, PEAK_PRICE, PROPOSAL_PREFIX, TELEMETRY_TOPIC)

AGENTS = {"load", "generation", "storage", "pricing"}


def decide(t, p):
    """Merge telemetry and the four proposals into one dispatch decision.
    Priority order: essential load > battery limits > solar self-use > peak avoidance."""
    load, solar = t["load_kw"], t["solar_kw"]
    soc, price = t["battery_soc"], t["price_per_kwh"]
    load_p, stor_p = p["load"], p["storage"]

    # 1. Essential load is always served. Flexible load is shed only at peak price.
    shed = load_p["recommended_action"] == "SHED_FLEXIBLE_LOAD" and price >= PEAK_PRICE
    active = load_p["essential_load_kw"] if shed else load
    shed_kw = round(load - active, 2)

    # 2. Solar serves the active load first.
    solar_to_load = round(min(solar, active), 2)
    surplus = round(solar - solar_to_load, 2)

    # 3. Surplus charges the battery only if the storage agent allows it and SOC is below the ceiling.
    to_battery = 0.0
    if stor_p["recommended_action"] == "CHARGE" and soc < MAX_SOC:
        to_battery = round(min(surplus, stor_p["recommended_power_kw"], MAX_BATTERY_KW), 2)
    exported = round(surplus - to_battery, 2)

    # 4. Remaining load: battery only if the storage agent allows discharge and SOC is above the floor.
    remaining = round(active - solar_to_load, 2)
    from_battery = 0.0
    if remaining > 0 and stor_p["recommended_action"] == "DISCHARGE" and soc > MIN_SOC:
        from_battery = round(min(remaining, stor_p["recommended_power_kw"], MAX_BATTERY_KW), 2)
    grid = round(remaining - from_battery, 2)

    summary = (f"Hour {t['hour']:02d}:00 | Load {active:.2f} kW (shed {shed_kw:.2f}) | "
               f"Solar {solar_to_load:.2f} kW | Battery {from_battery:.2f} kW | Grid {grid:.2f} kW")

    return {
        "hour": t["hour"],
        "active_load_kw": round(active, 2),
        "load_shed_kw": shed_kw,
        "solar_to_load_kw": solar_to_load,
        "solar_to_battery_kw": to_battery,
        "solar_exported_kw": exported,
        "battery_to_load_kw": from_battery,
        "grid_import_kw": grid,
        "grid_price_per_kwh": price,
        "summary": summary,
    }


class Coordinator:
    def __init__(self):
        self.telemetry = None
        self.proposals = {}
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="coordinator")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def on_connect(self, client, userdata, flags, reason_code, properties=None):
        client.subscribe(TELEMETRY_TOPIC)
        client.subscribe(PROPOSAL_PREFIX + "#")
        print("[COORDINATOR] connected", flush=True)

    def on_message(self, client, userdata, msg):
        try:
            data = json.loads(msg.payload.decode())
            if msg.topic == TELEMETRY_TOPIC:          # new hour: wait for its proposals
                self.telemetry = data
                self.proposals = {}
                return
            if self.telemetry is None or data.get("hour") != self.telemetry["hour"]:
                return                                 # stale or early proposal
            self.proposals[data["agent"]] = data
            if AGENTS.issubset(self.proposals):
                decision = decide(self.telemetry, self.proposals)
                client.publish(DECISION_TOPIC, json.dumps(decision))
                print("[COORDINATOR]", decision["summary"], flush=True)
                self.proposals = {}
        except Exception as exc:
            print(f"[COORDINATOR ERROR] {exc}", flush=True)

    def run(self):
        self.client.connect(BROKER_HOST, BROKER_PORT, 60)
        self.client.loop_forever()


if __name__ == "__main__":
    Coordinator().run()