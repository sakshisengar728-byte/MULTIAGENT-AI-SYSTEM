import json
import time
import threading

import paho.mqtt.client as mqtt

from config import (
    BROKER_HOST,
    BROKER_PORT,
    DECISION_TOPIC,
    TELEMETRY_TOPIC
)
from energy_simulator import EnergySimulator


class DispatchGuard:
    def __init__(self, sim):
        self.sim = sim
        self.pending_step_id = None
        self.lock = threading.Lock()
        self.completed = threading.Event()

    def prepare(self, reading):
        with self.lock:
            self.completed.clear()
            self.pending_step_id = reading["step_id"]

    def apply(self, decision):
        with self.lock:
            if self.pending_step_id is None:
                return False

            if decision.get("step_id") != self.pending_step_id:
                return False

            self.sim.apply_dispatch(decision)
            self.pending_step_id = None
            self.completed.set()
            return True


def main():
    sim = EnergySimulator()
    guard = DispatchGuard(sim)
    ready = threading.Event()

    def on_connect(client, userdata, flags,
                   reason_code, properties=None):
        client.subscribe(DECISION_TOPIC)
        print("[SIMULATOR] connected to broker", flush=True)

    def on_subscribe(client, userdata, mid,
                     reason_codes, properties=None):
        if all(not code.is_failure for code in reason_codes):
            ready.set()

    def on_message(client, userdata, msg):
        try:
            decision = json.loads(msg.payload.decode())

            if guard.apply(decision):
                print("[SIMULATOR] Dispatch applied:",
                      decision["step_id"], flush=True)
            else:
                print("[SIMULATOR] Stale or duplicate decision ignored",
                      flush=True)

        except Exception as exc:
            print("[SIMULATOR ERROR]", exc, flush=True)

    client = mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION2,
        client_id="simulator"
    )

    client.on_connect = on_connect
    client.on_subscribe = on_subscribe
    client.on_message = on_message

    client.connect(BROKER_HOST, BROKER_PORT, 60)
    client.loop_start()

    try:
        if not ready.wait(timeout=15):
            raise RuntimeError("MQTT subscription not ready")

        print("Synchronized simulation started.", flush=True)

        while True:
            started = time.monotonic()

            reading = sim.step()
            guard.prepare(reading)

            client.publish(
                TELEMETRY_TOPIC,
                json.dumps(reading)
            )

            print(
                f"Hour {reading['hour']:02d}:00 | "
                f"Load {reading['load_kw']} kW | "
                f"Solar {reading['solar_kw']} kW | "
                f"SOC {reading['battery_soc']}%",
                flush=True
            )

            if not guard.completed.wait(timeout=30):
                print(
                    "[SIMULATOR ERROR] Dispatch timeout. Restarting simulator.",
                    flush=True
                )
                raise RuntimeError("MQTT dispatch timeout")

            elapsed = time.monotonic() - started
            time.sleep(max(0, 3 - elapsed))

    except KeyboardInterrupt:
        print("Simulator stopped.")

    finally:
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()
