import json
import threading
import time
import urllib.request
import urllib.error

import paho.mqtt.client as mqtt

from config import (BROKER_HOST, BROKER_PORT, DECISION_TOPIC, EXPLANATION_TOPIC,
                    OLLAMA_MODEL, OLLAMA_URL, GROQ_API_KEY,
                    GROQ_MODEL, GROQ_URL, LLM_INTERVAL)

latest = {"decision": None}     # only the newest decision is explained
lock = threading.Lock()


def template_explanation(d):
    """Fallback text used when the local LLM is not running."""
    return (f"At {d['hour']:02d}:00, solar supplied {d['solar_to_load_kw']} kW, the battery "
            f"supplied {d['battery_to_load_kw']} kW, and the grid supplied {d['grid_import_kw']} kW. "
            f"Flexible load shed: {d['load_shed_kw']} kW.")


def ollama_explanation(d):
    prompt = ("You explain the energy dispatch decision of a home microgrid to the homeowner. "
              "Write exactly two plain sentences. Use only the numbers in the JSON. "
              "All electricity tariffs are in Indian Rupees (INR). "
              "Never use dollars or USD. "
              "Mention the simulation hour in the explanation. "

    "The active_load_kw is the actual served load. "
    "The load_shed_kw is the total unserved flexible load. "
    "Never subtract load_shed_kw from active_load_kw. "
    "Solar, battery and grid together supply the active load. "
    "Solar charging and solar export are not household load supply. "
    "Do not claim that all demand was served when load shedding occurred. "
    "Do not invent savings, percentages or energy values. "
"Do not invent numbers.\n\nDecision JSON:\n" + json.dumps(d))
    body = json.dumps({"model": OLLAMA_MODEL, "prompt": prompt, "stream": False,
                       "options": {"temperature": 0.2}}).encode()
    req = urllib.request.Request(OLLAMA_URL, data=body,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read().decode())["response"].strip()


def groq_explanation(d):
    prompt = (
        "Explain this home microgrid energy decision "
        "in exactly two simple sentences. "
        "Use only the supplied data. Do not invent numbers. "
        "All electricity tariffs are in Indian Rupees (INR). "
        "Always express electricity prices in INR or Rs. per kWh. "
        "Never use dollars or USD. "
        "Mention the simulation hour in the explanation. "

    "The active_load_kw is the actual served load. "
    "The load_shed_kw is the total unserved flexible load. "
    "Never subtract load_shed_kw from active_load_kw. "
    "Solar, battery and grid together supply the active load. "
    "Solar charging and solar export are not household load supply. "
    "Do not claim that all demand was served when load shedding occurred. "
    "Do not invent savings, percentages or energy values. "

        + json.dumps(d)
    )

    body = json.dumps({
        "model": GROQ_MODEL,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2,
        "max_completion_tokens": 1024,
        "reasoning_effort": "low"
    }).encode()

    req = urllib.request.Request(
        GROQ_URL,
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer " + GROQ_API_KEY,
            "User-Agent": "MultiAgentEnergySystem/1.0",
            "Accept": "application/json"
        }
    )

    with urllib.request.urlopen(req, timeout=30) as resp:
        result = json.loads(resp.read().decode())
        answer = result["choices"][0]["message"]["content"].strip()
        if not answer:
            raise ValueError("Empty LLM response; finish_reason=" + str(result["choices"][0].get("finish_reason")))
        return answer


def llm_explanation(d):
    if GROQ_API_KEY:
        return groq_explanation(d)
    return ollama_explanation(d)


def explain(d):
    try:
        text = llm_explanation(d)
        provider = "Groq" if GROQ_API_KEY else "Ollama"
        print(f"[LLM PROVIDER] {provider}", flush=True)
        return {
            "source": "llm",
            "hour": d["hour"],
            "text": text
        }
    except urllib.error.HTTPError as e:
        detail = e.read(2048).decode("utf-8", errors="replace")
        if GROQ_API_KEY:
            detail = detail.replace(GROQ_API_KEY, "[REDACTED]")
        print(f"[LLM HTTP DETAIL] {e.code}: {detail}", flush=True)
        return {
            "source": "template",
            "hour": d["hour"],
            "text": template_explanation(d)
        }
    except Exception as e:
        print(f"[LLM ERROR] {type(e).__name__}: {e}", flush=True)
        return {
            "source": "template",
            "hour": d["hour"],
            "text": template_explanation(d)
        }


def worker(client):
    """Runs the slow LLM calls in a separate thread, so the decision loop never waits."""
    while True:
        with lock:
            d, latest["decision"] = latest["decision"], None
        if d is None:
            time.sleep(0.5)
            continue
        result = explain(d)
        result["text"] = (
            f"Explanation for simulation hour: {d['hour']:02d}:00\n\n"
            + result["text"]
        )
        client.publish(EXPLANATION_TOPIC, json.dumps(result))
        print(f"[LLM:{result['source']}] {result['text']}", flush=True)
        if GROQ_API_KEY:
            time.sleep(LLM_INTERVAL)


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