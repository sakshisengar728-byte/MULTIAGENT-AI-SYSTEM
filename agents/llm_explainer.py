import json
import threading
import time
import urllib.request

import paho.mqtt.client as mqtt

from config import (BROKER_HOST, BROKER_PORT, DECISION_TOPIC, EXPLANATION_TOPIC,
                    OLLAMA_MODEL, OLLAMA_URL)

latest = {"decision": None}     # only the newest decision is explained
lock = threading.Lock()


def template_explanation(d):
    """Fallback text used when the local LLM is not running."""
    return (f"At {d['hour']:02d}:00, solar supplied {d['solar_to_load_kw']} kW, the battery "
            f"supplied {d['battery_to_load_kw']} kW, and the grid supplied {d['grid_import_kw']} kW. "
            f"Flexible load shed: {d['load_shed_kw']} kW.")


def llm_explanation(d):
    prompt = ("You explain the energy dispatch decision of a home microgrid to the homeowner. "
              "Write exactly two plain sentences. Use only the numbers in the JSON. "
              "Do not invent numbers.\n\nDecision JSON:\n" + json.dumps(d))
    body = json.dumps({"model": OLLAMA_MODEL, "prompt": prompt, "stream": False,
                       "options": {"temperature": 0.2}}).encode()
    req = urllib.request.Request(OLLAMA_URL, data=body,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read().decode())["response"].strip()


def explain(d):
    try:
        return {"source": "llm", "hour": d["hour"], "text": llm_explanation(d)}
    except Exception:
        return {"source": "template", "hour": d["hour"],
                "text": template_explanation(d) + " (LLM unavailable, showing template text.)"}


def worker(client):
    """Runs the slow LLM calls in a separate thread, so the decision loop never waits."""
    while True:
        with lock:
            d, latest["decision"] = latest["decision"], None
        if d is None:
            time.sleep(0.5)
            continue
        result = explain(d)
        client.publish(EXPLANATION_TOPIC, json.dumps(result))
        print(f"[LLM:{result['source']}] {result['text']}", flush=True)


def on_connect(client, userdata, flags, reason_code, properties=None):
    client.subscribe(DECISION_TOPIC)


def on_message(client, userdata, msg):
    with lock:
        latest["decision"] = json.loads(msg.payload.decode())


def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="llm_explainer")
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER_HOST, BROKER_PORT, 60)
    threading.Thread(target=worker, args=(client,), daemon=True).start()
    client.loop_forever()


if __name__ == "__main__":
    main()