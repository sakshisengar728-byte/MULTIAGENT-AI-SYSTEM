import json
import time

import paho.mqtt.client as mqtt

from config import BROKER_HOST, BROKER_PORT, DECISION_TOPIC, TELEMETRY_TOPIC
from energy_simulator import EnergySimulator


def main():
    sim = EnergySimulator()

    def on_connect(client, userdata, flags, reason_code, properties=None):
        client.subscribe(DECISION_TOPIC)
        print("[SIMULATOR] connected to broker")

    def on_message(client, userdata, msg):
        sim.apply_dispatch(json.loads(msg.payload.decode()))

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="simulator")
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER_HOST, BROKER_PORT, 60)
    client.loop_start()

    print("Publishing one simulated hour every 3 seconds.")
    try:
        while True:
            reading = sim.step()
            client.publish(TELEMETRY_TOPIC, json.dumps(reading))
            print(f"Hour {reading['hour']:02d}:00 | load {reading['load_kw']} kW | "
                  f"solar {reading['solar_kw']} kW | SOC {reading['battery_soc']}% | "
                  f"price Rs. {reading['price_per_kwh']}")
            time.sleep(3)
    except KeyboardInterrupt:
        print("Simulator stopped.")
    finally:
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()