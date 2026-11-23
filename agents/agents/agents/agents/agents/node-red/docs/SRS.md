# Software Requirements Specification (SRS)

## Multi-Agent AI System for IoT Energy Management

| Field | Detail |
|---|---|
| Project | Multi-Agent AI System for IoT Energy Management |
| Version | 1.0 |
| Date | November 2026 |
| Author | [YOUR_NAME], [ROLL_NO] |
| Institution | [COLLEGE_NAME], HCLTech Training Program |
| Source code | [GITHUB_LINK] |
| Live dashboard | [LIVE_LINK] |
| Demo video | [VIDEO_LINK] |

---

## 1. Introduction

### 1.1 Purpose

This document specifies the requirements, interfaces, design and verification of a multi-agent system that manages the energy of a simulated smart-home microgrid. It is written for evaluators, the developer, and anyone who extends the project.

### 1.2 Scope

The system simulates a home with rooftop solar (5 kW peak), battery storage (10 kWh), household load (1.5 to 3.5 kW) and a time-of-use tariff. For each simulated hour, four agents propose actions and a coordinator decides. A local LLM explains the decision, Node-RED raises grid-import alerts, and a web dashboard shows the results. Physical hardware, live weather data and reactive power are out of scope.

### 1.3 Definitions

| Term | Meaning |
|---|---|
| MQTT | Lightweight publish/subscribe messaging protocol for IoT |
| Broker | Server that routes MQTT messages (Eclipse Mosquitto) |
| Agent | Software component that observes telemetry and proposes an action |
| BDI | Belief–Desire–Intention model used to structure agent reasoning |
| SOC | State of charge of the battery, in percent |
| TOU | Time-of-use tariff: the price depends on the hour of the day |
| LLM | Large language model; here a small model run locally with Ollama |
| Essential load | Load that must always be served (1.2 kW) |

### 1.4 References

1. Wooldridge, M. (2009). *An Introduction to Multi-Agent Systems* (2nd ed.). John Wiley & Sons.
2. OASIS (2019). *MQTT Version 5.0*. https://docs.oasis-open.org/mqtt/mqtt/v5.0/mqtt-v5.0.html
3. Colmenar-Santos, A., et al. (2016). Energy storage systems in smart grids. *Renewable and Sustainable Energy Reviews*, 65, 1075–1094.
4. Eclipse Mosquitto. https://mosquitto.org/
5. Ollama. https://ollama.com/
6. Node-RED. https://nodered.org/
7. Chart.js. https://www.chartjs.org/

---

## 2. Overall Description

### 2.1 Architecture

```
Simulator ──telemetry──► Mosquitto broker ──► Load, Solar, Storage, Pricing agents
                                  ▲                        │
                                  │                  proposals
                                  │                        ▼
                                  └──────decision──── Coordinator
                                                           │
                    ┌──────────────────────────────────────┼──────────────────┐
                    ▼                                      ▼                  ▼
          Simulator (battery update)            LLM explainer         Node-RED (grid alert)
                                                           │
                                                           ▼
                                          Web dashboard (all topics via MQTT)
```

### 2.2 Components

| Component | File(s) | Role |
|---|---|---|
| Simulator | `energy_simulator.py`, `mqtt_simulator.py` | Creates one hour of readings, publishes telemetry, updates the battery from each decision |
| Broker | `mosquitto.conf` | Message bus on port 1883 |
| Agents | `agents/*.py` | Four BDI-style agents: load, solar, storage, pricing |
| Coordinator | `coordinator.py` | Merges proposals under safety rules |
| LLM explainer | `llm_explainer.py` | Plain-language explanation, with template fallback |
| Node-RED | `node-red/flows.json` | Grid-import alert |
| Dashboard | `dashboard.py`, `index.html` | Web page and JSON API |
| Launcher | `run_system.py` | Starts all services and restarts any that crash |
| Tests | `test_system.py` | Automated verification |

### 2.3 User classes

| User | Purpose |
|---|---|
| Homeowner | Reads the dashboard and the plain-language explanation |
| Evaluator | Runs the tests, opens the live dashboard, reads the documentation |
| Developer | Changes agent rules or settings in `config.py` |

### 2.4 Operating environment

- **Development:** Windows 10 or 11, Python 3.13, paho-mqtt 2.1.0, Mosquitto 2.x. Optional: Node.js with Node-RED, and Ollama with llama3.2:3b.
- **Live deployment:** Docker container (`python:3.13-slim`) that includes Mosquitto, hosted on Render's free web service.

### 2.5 Constraints

- Battery SOC must stay between 20% and 90%.
- Battery charge and discharge power must not exceed 2.5 kW.
- The essential load of 1.2 kW is never shed.
- Peak tariff is Rs. 8.0/kWh for hours 17 to 21 inclusive. Off-peak is Rs. 4.0/kWh.
- All settings are in `config.py`. The code contains no personal file paths.
- The free cloud plan has 512 MB of memory and sleeps after about 15 minutes without web traffic.

### 2.6 Assumptions

- One simulated hour is processed every 3 real seconds.
- Building load is uniformly random between 1.5 and 3.5 kW each hour.
- Solar output is 5 kW × max(0, 1 − |hour − 12| / 6). It is zero at 06:00 and 18:00 and peaks at 12:00.
- Charging efficiency is 95%. Discharge losses are ignored.
- The battery starts at 70% SOC.

---

## 3. Functional Requirements

| ID | Requirement | Priority |
|---|---|---|
| FR-01 | The simulator shall produce one hourly reading (load, solar, SOC, tariff, grid import). | Must |
| FR-02 | The simulator shall publish each reading as JSON to `energy/sensors/telemetry` every 3 seconds. | Must |
| FR-03 | Each of the four agents shall publish one proposal for each telemetry message. | Must |
| FR-04 | The coordinator shall wait for the four proposals of the same hour and publish one decision to `energy/coordinator/decision`. | Must |
| FR-05 | The essential load (1.2 kW) shall never be shed. | Must |
| FR-06 | Flexible load shall be shed only when the tariff is Rs. 8.0/kWh or more and flexible load exceeds 0.3 kW. | Must |
| FR-07 | The battery shall not discharge when SOC is 20% or lower. | Must |
| FR-08 | The battery shall not charge when SOC is 90% or higher. | Must |
| FR-09 | Battery charge and discharge power shall not exceed 2.5 kW. | Must |
| FR-10 | Solar shall serve the active load first, charge the battery with any surplus, and export the remainder. | Must |
| FR-11 | The simulated SOC shall be updated from each decision (closed loop). | Should |
| FR-12 | The dashboard shall show live readings, each agent's proposal and reason, the coordinator decision, the explanation, the latest grid alert, and a 24-hour trend. | Must |
| FR-13 | A local LLM shall explain each decision in plain language. | Should |
| FR-14 | If the LLM is unavailable, the system shall show template text and keep running. | Must |
| FR-15 | Node-RED shall raise an alert when grid import is above 0 kW and publish it to `energy/alerts/grid`. | Should |
| FR-16 | Automated tests shall verify the three scenarios, essential-load protection, SOC limits and the LLM fallback. | Must |
| FR-17 | The launcher shall restart any service that stops unexpectedly. | Should |

## 4. Non-Functional Requirements

| ID | Category | Requirement |
|---|---|---|
| NFR-01 | Performance | A decision shall be published within each 3-second cycle. The dashboard shall refresh every 1.5 seconds. |
| NFR-02 | Reliability | An LLM failure shall not stop the decision loop. The LLM runs in its own thread. |
| NFR-03 | Portability | The project shall contain no personal file paths and shall run in Docker. |
| NFR-04 | Maintainability | Settings shall be in `config.py`. Each agent shall inherit from `BaseAgent`. |
| NFR-05 | Availability | The live link works while the Render service is awake. The free plan may sleep after inactivity. |
| NFR-06 | Security | The broker listens only on 127.0.0.1 inside the container. Only the HTTP dashboard is public. The system stores no personal data. |
| NFR-07 | Usability | The dashboard runs in any modern browser without installation. |

## 5. External Interface Requirements

### 5.1 MQTT topics

| Topic | Publisher | Subscribers | Payload |
|---|---|---|---|
| `energy/sensors/telemetry` | Simulator | Agents, coordinator, dashboard | Hourly reading (JSON) |
| `energy/proposals/load`, `/generation`, `/storage`, `/pricing` | Agents | Coordinator, dashboard | Proposal (JSON) |
| `energy/coordinator/decision` | Coordinator | Simulator, LLM explainer, dashboard, Node-RED | Dispatch decision (JSON) |
| `energy/llm/explanation` | LLM explainer | Dashboard | Text and source (`llm` or `template`) |
| `energy/alerts/grid` | Node-RED | Dashboard | Alert text (JSON) |

Example telemetry message:

```json
{"timestamp": "2026-11-23 12:00:00", "hour": 12, "load_kw": 2.2, "solar_kw": 4.8,
 "battery_soc": 55.0, "battery_energy_kwh": 5.5, "grid_kw": 0.0,
 "price_per_kwh": 4.0, "currency": "INR"}
```

### 5.2 HTTP interface

- `GET /` returns the dashboard page.
- `GET /api/state` returns the latest telemetry, decision, proposals, explanation, alert and 24-hour history as JSON.
- Local port: 8050 (127.0.0.1). On Render: the port given by the `PORT` variable, bound to 0.0.0.0.

### 5.3 Other interfaces

- **Ollama:** `POST http://127.0.0.1:11434/api/generate` with model `llama3.2:3b`.
- **Node-RED:** editor at `http://localhost:1880`. Flow file: `node-red/flows.json`.

---

## 6. System Design

### 6.1 Agent design (BDI pattern)

| Agent | Beliefs (inputs) | Desires | Intention (proposal) |
|---|---|---|---|
| Load | Load, tariff | Keep the essential load on. Shed flexible load at peak price. | `SHED_FLEXIBLE_LOAD` or `MAINTAIN_NORMAL_LOAD` |
| Solar | Solar output, load | Use solar directly. Store the surplus. | `SUPPLY_LOAD_AND_STORE_SURPLUS`, `OFFSET_PORTION_OF_LOAD` or `STANDBY` |
| Storage | SOC, solar, load, tariff | Keep SOC between 20% and 90%. Limit power to 2.5 kW. | `CHARGE`, `HOLD_FULL`, `DISCHARGE`, `HOLD_EMPTY` or `HOLD` |
| Pricing | Tariff, hour | Classify the tariff period. | `MINIMIZE_GRID_IMPORT`, `ALLOW_GRID_OR_PRE_CHARGE` or `MAXIMIZE_SOLAR_SELF_CONSUMPTION` |

### 6.2 Coordinator priorities

1. Essential load guarantee.
2. Battery safety limits (SOC 20–90%, power 2.5 kW maximum).
3. Solar self-consumption.
4. Peak-tariff avoidance.

The coordinator follows the storage agent's charge and discharge recommendations and checks the safety limits again before dispatch.

### 6.3 Message flow (per simulated hour)

1. The simulator publishes telemetry.
2. The four agents publish proposals.
3. The coordinator publishes one decision.
4. The simulator updates the battery from the decision.
5. The LLM explainer writes an explanation.
6. Node-RED checks for grid import and publishes an alert if needed.
7. The dashboard updates.

---

## 7. Verification

### 7.1 Automated tests (`python -m pytest -v`)

| Test | Input | Expected result | Requirements |
|---|---|---|---|
| `test_scenario_a_noon_solar_surplus` | Hour 12, load 2.2 kW, solar 4.8 kW, SOC 55%, Rs. 4 | Solar to load 2.2 kW, to battery 2.5 kW, exported 0.1 kW, grid 0 kW | FR-04, FR-10 |
| `test_scenario_b_evening_peak_tariff` | Hour 18, load 3.0 kW, solar 0, SOC 75%, Rs. 8 | Shed 1.8 kW, battery 1.2 kW, grid 0 kW | FR-04, FR-06 |
| `test_scenario_c_low_battery_guard` | Hour 20, load 2.5 kW, solar 0, SOC 18%, Rs. 8 | Battery 0 kW (blocked), shed 1.3 kW, grid 1.2 kW | FR-07 |
| `test_essential_load_is_never_shed` | Hour 19, load 2.5 kW, solar 0, SOC 80%, Rs. 8 | Active load at least 1.2 kW | FR-05 |
| `test_battery_soc_stays_within_limits` | Charge from 89%; discharge from 21% | SOC stays within 20–90% | FR-07, FR-08, FR-11 |
| `test_llm_fallback_text_contains_numbers` | Template explanation for a decision | Text contains the numbers | FR-14 |

Result: [TEST_RESULT] (for example, "6 passed").

### 7.2 Manual tests

| Test | Steps | Expected result | Requirements |
|---|---|---|---|
| Live run (laptop) | Run `python run_system.py`, open the dashboard | Values change every 3 seconds. The chart fills over 24 steps. | FR-01, FR-02, FR-12 |
| LLM offline | Quit Ollama and wait for the next decision | Badge shows `template`. Dispatch continues. | FR-13, FR-14 |
| Node-RED alert | Deploy `flows.json`, wait for an off-peak hour | Alert appears in the Node-RED debug panel and on the dashboard | FR-15 |
| Public link | Open the Render link on mobile data | Dashboard loads and values update | NFR-05 |
| Crash recovery | Close one agent window (laptop run) | `run_system.py` prints a restart message | FR-17 |

---

## 8. Deployment

- The repository is on GitHub. Render deploys it automatically from the `Dockerfile` on every commit to `main`.
- The container starts Mosquitto (`start.sh`), waits until the broker accepts connections, and then runs `run_system.py`.
- The dashboard binds to `0.0.0.0` on the port Render provides.
- The LLM and Node-RED run on the developer's laptop for the demo video. The live link shows the template explanation and the "No grid alert yet" message.

---

## 9. Known Limitations

- The data is simulated. There is no physical meter and no live weather data.
- Reactive power, power factor and phase imbalance are not modelled.
- The battery uses a constant charge efficiency. Temperature and voltage effects are not modelled.
- The LLM is advisory only. Dispatch never depends on it.
- The free cloud plan can sleep. Each restart begins the simulated day at 00:00 with the battery at 70%.
- One simulated hour passes every 3 real seconds, so the 24-hour trend takes about 72 seconds to fill.
- Under heavy load, a decision can occasionally be skipped if a message arrives out of order. The next hour then continues normally.

## 10. Future Scope

- Hardware-in-the-loop testing with an ESP32 or Arduino and a Modbus energy meter.
- Solar forecasting with an LSTM model using a real weather API.
- Explanations based on past decisions, not only the current one.

---

## 11. Appendix

**A. AI tools disclosure:** [Same wording as the README.]

**B. Links**
- Source code: [GITHUB_LINK]
- Live dashboard: [LIVE_LINK]
- Demo video: [VIDEO_LINK]