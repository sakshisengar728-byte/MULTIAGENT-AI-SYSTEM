import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

import paho.mqtt.client as mqtt

from config import (ALERT_TOPIC, BROKER_HOST, BROKER_PORT, DASHBOARD_HOST, DASHBOARD_PORT,
                    DECISION_TOPIC, EXPLANATION_TOPIC, PROPOSAL_PREFIX, TELEMETRY_TOPIC)

HTML = (Path(__file__).parent / "index.html").read_bytes()

lock = threading.Lock()
state = {
    "telemetry": {},
    "decision": {},
    "proposals": {},
    "explanation": {},
    "alert": None,
    "history": [],
}


def on_connect(client, userdata, flags, reason_code, properties=None):
    client.subscribe("energy/#")


def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        with lock:
            if msg.topic == TELEMETRY_TOPIC:
                state["telemetry"] = data
            elif msg.topic == DECISION_TOPIC:
                state["decision"] = data
                t = state["telemetry"]
                state["history"].append({
                    "hour": f"{data['hour']:02d}:00",
                    "load": t.get("load_kw", 0),
                    "solar": t.get("solar_kw", 0),
                    "soc": t.get("battery_soc", 0),
                    "grid": data["grid_import_kw"],
                })
                state["history"] = state["history"][-24:]
            elif msg.topic == EXPLANATION_TOPIC:
                state["explanation"] = data
            elif msg.topic == ALERT_TOPIC:
                state["alert"] = data
            elif msg.topic.startswith(PROPOSAL_PREFIX):
                state["proposals"][data["agent"]] = data
    except Exception as exc:
        print(f"[DASHBOARD ERROR] {exc}", flush=True)


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/":
            body, ctype = HTML, "text/html; charset=utf-8"
        elif path == "/api/state":
            with lock:
                body = json.dumps(state).encode("utf-8")
            ctype = "application/json"
        else:
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass    # keep the logs quiet


def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="dashboard")
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER_HOST, BROKER_PORT, 60)
    client.loop_start()

    server = ThreadingHTTPServer((DASHBOARD_HOST, DASHBOARD_PORT), Handler)
    print(f"Dashboard running on port {DASHBOARD_PORT}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()