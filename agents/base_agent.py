import json

import paho.mqtt.client as mqtt

from config import BROKER_HOST, BROKER_PORT, PROPOSAL_PREFIX, TELEMETRY_TOPIC


class BaseAgent:
    """Shared MQTT code. Each agent sets `name` and implements evaluate()."""

    name = "base"

    def __init__(self):
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2,
                                  client_id=f"{self.name}_agent")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def on_connect(self, client, userdata, flags, reason_code, properties=None):
        client.subscribe(TELEMETRY_TOPIC)
        print(f"[{self.name.upper()} AGENT] connected, listening for telemetry", flush=True)

    def on_message(self, client, userdata, msg):
        try:
            telemetry = json.loads(msg.payload.decode())
            proposal = self.evaluate(telemetry)
            proposal["agent"] = self.name
            proposal["hour"] = telemetry["hour"]
            proposal["step_id"] = telemetry["step_id"]
            client.publish(PROPOSAL_PREFIX + self.name, json.dumps(proposal))
            print(f"[{self.name.upper()} AGENT] {telemetry['hour']:02d}:00 -> {proposal}", flush=True)
        except Exception as exc:
            print(f"[{self.name.upper()} AGENT ERROR] {exc}", flush=True)

    def evaluate(self, telemetry):
        raise NotImplementedError

    def run(self):
        self.client.connect(BROKER_HOST, BROKER_PORT, 60)
        self.client.loop_forever()