# MULTIAGENT-AI-SYSTEM
# Multi-Agent AI System for IoT Energy Management

A simulated smart-home microgrid with rooftop solar, battery storage, household load and a time-of-use tariff. Four Python agents propose actions over MQTT, a coordinator enforces safety rules, a local LLM explains each decision, Node-RED raises grid-import alerts, and a live web dashboard shows everything.

| Link | URL |
|---|---|
| Live dashboard | [LIVE_LINK] |
| Demo video (LLM and Node-RED) | [VIDEO_LINK] |
| Software Requirements Specification | [docs/SRS.md](docs/SRS.md) |

## Technologies

Python 3.13 · paho-mqtt · Eclipse Mosquitto · Ollama (llama3.2:3b) · Node-RED · Chart.js · Docker · Render

## How it works

1. The simulator publishes one simulated hour every 3 seconds to `energy/sensors/telemetry`.
2. Four agents (load, solar, storage, pricing) each publish a proposal to `energy/proposals/<agent>`.
3. The coordinator merges the proposals into one decision on `energy/coordinator/decision`. Priorities: essential load, battery limits, solar self-use, peak-tariff avoidance.
4. The decision updates the simulated battery, the LLM explainer, Node-RED and the dashboard.

## Project structure

```
MultiAgent-IoT-Energy-Management/
├── agents/                 four agents and the shared base class
├── node-red/flows.json     Node-RED grid-alert flow
├── docs/SRS.md             requirements document
├── config.py               all settings
├── energy_simulator.py     simulated microgrid
├── mqtt_simulator.py       publishes telemetry
├── coordinator.py          decision logic
├── llm_explainer.py        local LLM explanations
├── dashboard.py            web server
├── index.html              dashboard page
├── run_system.py           starts and supervises all services
├── test_system.py          automated tests
├── Dockerfile              cloud deployment
├── start.sh                container start script
├── mosquitto.conf          MQTT broker settings
└── requirements.txt
```

## Run on your computer (Windows)

Mosquitto must be running first (`services.msc` → Mosquitto Broker → Start).

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m pytest -v
python run_system.py
```

Open http://localhost:8050. Optional extras: Ollama (`ollama pull llama3.2:3b`) for LLM explanations, and Node-RED with `node-red/flows.json` for grid alerts.

## Tests

`python -m pytest -v` runs 6 automated tests. They cover the three microgrid scenarios, essential-load protection, battery limits and the LLM fallback.

## Deployment

The live dashboard runs on Render as a Docker container. The container includes the Mosquitto broker and all Python services. Ollama and Node-RED cannot run on the free cloud server, so the live dashboard shows the template explanation and "No grid alert yet". The demo video shows both running on a laptop.

## AI tools disclosure

[REFERENCES FROM:ChatGPT or Claude.] They helped draft code and documentation. The author reviewed, tested and integrated all components.

## Author

[SAKSHI SENGAR], [2400320310150], [ABES ENGINEERING COLLEGE], HCLTech Training Program