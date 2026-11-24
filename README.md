# Multi-Agent AI System for IoT Energy Management

## Project Details

| Particular | Details |
|---|---|
| Student Name | Sakshi Sengar |
| Project ID | P_308 |
| College | ABES Engineering College, Ghaziabad |
| Course | B.Tech |
| Branch | Electronics and Communication Engineering |
| Year | Third Year |
| Section | C |
| Domain | Embedded IoT |
| Program | HCLTech Training Program |
| Submission | November 2026 |

## Project Links

- [Live Dashboard](https://multiagent-ai-system-6cri.onrender.com)
- [GitHub Repository](https://github.com/sakshisengar728-byte/MULTIAGENT-AI-SYSTEM)
- [Verified Deployment Commit](https://github.com/sakshisengar728-byte/MULTIAGENT-AI-SYSTEM/commit/ddff468)

## Project Overview

This project implements a multi-agent energy management system for a simulated smart-home microgrid consisting of solar photovoltaic generation, battery energy storage, household electricity demand and time-of-use electricity tariffs.

Four independent Python agents communicate through MQTT. A central coordinator processes their proposals and applies rule-based energy management decisions while protecting essential loads and enforcing battery operating limits.

Groq LLM generates plain-language explanations of energy decisions. Node-RED provides automated grid-import alerts, while a live web dashboard displays energy consumption, battery status, agent proposals, electricity costs and performance graphs.

## Key Features

- Four independent energy management agents
- Centralized decision-making coordinator
- MQTT-based inter-agent communication
- Dynamic solar generation and electricity demand simulation
- Time-of-use electricity tariff management
- Essential-load protection
- Flexible-load shedding during peak tariff periods
- Battery charging and discharging safety
- Unique simulation step identifiers
- Synchronized MQTT dispatch
- Stale and duplicate decision protection
- Automatic simulator restart after dispatch timeout
- Groq cloud LLM integration
- Optional local Ollama integration
- Template-based fallback explanations
- Node-RED grid-import alerts
- Live web dashboard
- Python-based electricity cost analysis
- Electricity cost comparison bar chart
- Rolling 24-hour energy trend visualization
- Docker-based cloud deployment

## System Architecture

```text
                  ENERGY SIMULATOR
                         |
                  MQTT TELEMETRY
                         |
        +----------------+----------------+
        |                |                |
    Load Agent     Generation Agent      |
    Storage Agent    Pricing Agent       |
        |                |                |
        +----------------+----------------+
                         |
                 MQTT PROPOSALS
                         |
                CENTRAL COORDINATOR
                         |
                 DISPATCH DECISION
                         |
     +----------+--------+---------+----------+
     |          |                  |          |
  Battery    Groq LLM          Node-RED    Python
  Update    Explanation         Alerts   Cost Analysis
     |          |                  |          |
     +----------+------------------+----------+
                         |
                  LIVE DASHBOARD
                         |
                  RENDER CLOUD
```


## Programming Languages and Technologies

| Technology | Application |
|---|---|
| Python 3.13 | Agent logic, simulation, calculations and backend |
| HTML5 | Dashboard structure |
| CSS3 | Dashboard styling |
| JavaScript | Dynamic dashboard updates |
| JSON | MQTT messages and Node-RED configuration |
| Shell scripting | Container startup automation |
| MQTT | Inter-agent communication |
| Eclipse Mosquitto | MQTT message broker |
| Paho MQTT | Python MQTT client |
| Groq API | Cloud-based LLM explanations |
| Ollama | Optional local LLM |
| Node-RED | Automated grid-import alerts |
| Chart.js | Graphs and data visualization |
| Pytest | Automated software testing |
| Docker | Containerization |
| Git and GitHub | Version control and source code hosting |
| GitHub Codespaces | Cloud development and testing |
| Render | Live cloud deployment |

## Multi-Agent System

### 1. Load Agent

Monitors electricity demand, distinguishes essential and flexible loads, and recommends load shedding during peak tariff periods.

### 2. Generation Agent

Monitors simulated solar generation and recommends solar utilization and surplus energy management.

### 3. Storage Agent

Evaluates battery state of charge and recommends charging, discharging or holding based on energy availability, tariff and battery safety limits.

### 4. Pricing Agent

Evaluates electricity tariffs and recommends suitable energy utilization strategies.

### Central Coordinator

Collects all four agent proposals for the matching simulation step. It applies deterministic dispatch rules using telemetry and relevant proposals to protect essential loads, enforce battery limits and prioritize solar energy.

## System Configuration

| Parameter | Value |
|---|---|
| Battery capacity | 10 kWh |
| Minimum battery SOC | 20% |
| Maximum battery SOC | 90% |
| Initial battery SOC | 70% |
| Maximum battery power | 2.5 kW |
| Charging efficiency | 95% |
| Maximum simulated solar generation | 5 kW |
| Essential load | Up to 1.2 kW |
| Simulated building demand | 1.5 to 3.5 kW |
| Standard electricity tariff | INR 4/kWh |
| Peak electricity tariff | INR 8/kWh |
| Peak tariff period | 17:00 to 22:00 |
| Simulation interval | Approximately 3 seconds per simulated hour |
| Dispatch timeout | 30 seconds |
| LLM update interval | Approximately 30 seconds |
| MQTT port | 1883 |
| Local dashboard port | 8050 |

## MQTT Communication

| MQTT Topic | Purpose |
|---|---|
| energy/sensors/telemetry | Simulated energy readings |
| energy/proposals/# | Individual agent proposals |
| energy/coordinator/decision | Final dispatch decisions |
| energy/llm/explanation | AI-generated explanations |
| energy/alerts/grid | Node-RED grid alerts |

Unique step identifiers synchronize telemetry, agent proposals and dispatch decisions. The simulator waits for a matching dispatch before advancing to the next simulation step.

## Dataset and Simulation

The system uses a synthetic dataset generated dynamically through Python.

Building demand varies within the configured range. Solar generation follows a simulated daily sunlight profile, reaching maximum output around noon. Electricity tariffs depend on the simulated hour.

Battery SOC is updated according to the coordinator's charging and discharging decisions.

No physical IoT sensors or external historical electricity datasets are required for the current prototype.

## Electricity Cost Analysis

All electricity cost calculations are performed using Python.

- Original demand = Served load + Shed load
- Conventional cost = Original demand x Tariff x Duration
- Optimized cost = Grid import x Tariff x Duration
- Served-load baseline cost = Served load x Tariff x Duration
- Solar and battery savings = Served-load baseline cost - Optimized cost
- Load shedding reduction = Shed load x Tariff x Duration
- Total grid cost reduction = Conventional cost - Optimized cost
- Served-load savings percentage = Solar and battery savings / Served-load baseline cost x 100

The dashboard displays rolling 24-hour cost calculations and a graphical comparison of conventional and optimized grid expenditure.

## Verified Live Dashboard Results

The following results represent one captured 24-hour simulation window.

| Performance Metric | Result |
|---|---:|
| Conventional grid cost | INR 290.40 |
| Optimized grid cost | INR 102.72 |
| Solar and battery savings | INR 128.56 |
| Load shedding reduction | INR 59.12 |
| Total grid cost reduction | INR 187.68 |
| Overall grid cost reduction | 64.63% |
| Served-load savings | 55.59% |
| Grid energy imported | 25.68 kWh |
| Energy served | 51.82 kWh |
| Energy shed | 7.39 kWh |

These are simulated grid expenditure results, not actual electricity bill savings. Total cost reduction includes the effect of unserved flexible demand.

## Testing and Validation

| Test | Result |
|---|---|
| Python syntax validation | Passed |
| Automated unit tests | 6/6 Passed |
| 720-hour simulation test | Passed |
| Battery operating limit validation | Passed |
| Energy balance validation | Passed |
| Sequential step ID validation | Passed |
| Stale proposal rejection | Passed |
| Duplicate dispatch protection | Passed |
| MQTT synchronization | Passed |
| Docker integration testing | Passed |
| 24-hour dashboard verification | Passed |
| Automatic timeout recovery | Passed |
| Render deployment | Successful |
| Groq provider verification | Successful |
| Node-RED alert verification | Successful |

### Extended 720-Hour Simulation

A separate Python simulation test evaluated the dispatch algorithm over 720 simulated hours.

| Parameter | Result |
|---|---:|
| Total simulated hours | 720 |
| Minimum observed battery SOC | 33.71% |
| Maximum observed battery SOC | 90.00% |
| Total demand | 1796.78 kWh |
| Total served energy | 1599.43 kWh |
| Total unserved energy | 197.35 kWh |
| Total solar generation | 900.00 kWh |
| Total grid import | 791.85 kWh |
| Conventional grid cost | INR 8696.52 |
| Optimized grid cost | INR 3167.40 |
| Grid cost reduction | INR 5529.12 |
| Grid cost reduction percentage | 63.58% |

This extended test evaluated the Python simulation and dispatch logic directly, rather than running the complete MQTT deployment for 720 real hours.

## Project Structure

Main application files:

```text
MULTIAGENT-AI-SYSTEM/
├── README.md
├── .gitignore
└── agents/
    ├── base_agent.py
    ├── load_agent.py
    ├── generation_agent.py
    ├── storage_agent.py
    ├── pricing_agent.py
    ├── coordinator.py
    ├── config.py
    ├── energy_simulator.py
    ├── mqtt_simulator.py
    ├── battery_management.py
    ├── cost_analysis.py
    ├── llm_explainer.py
    ├── dashboard.py
    ├── index.html
    ├── run_system.py
    ├── test_system.py
    ├── requirements.txt
    ├── Dockerfile
    ├── .dockerignore
    ├── start.sh
    ├── mosquitto.conf
    └── node-red/
        ├── flows.json
        ├── settings.js
        ├── package.json
        └── package-lock.json
```

## Run Locally Using Docker

Install Docker and Git before running the following commands.

```bash
git clone https://github.com/sakshisengar728-byte/MULTIAGENT-AI-SYSTEM.git
cd MULTIAGENT-AI-SYSTEM
docker build -t multiagent-energy ./agents
docker run --rm -p 127.0.0.1:8050:8050 --name multiagent-energy multiagent-energy
```

Open the local dashboard:

http://localhost:8050

The Docker container starts Mosquitto, Node-RED and the Python services.

Without a configured LLM provider, the system can use template-based explanations.

## Run Automated Tests

```bash
cd agents
pip install -r requirements.txt
python -m pytest -v test_system.py
```

Expected result: 6 tests passed.

## Groq LLM Integration

The deployed system uses Groq API to generate natural-language explanations of coordinator decisions.

Configuration is provided through environment variables:

- GROQ_API_KEY
- GROQ_MODEL

API keys must be stored securely and must never be committed to the repository.

Groq integration was verified using Render application logs and live dashboard explanations.

The LLM explains decisions but does not directly control the energy dispatch algorithm.

## Node-RED Integration

Node-RED subscribes to MQTT dispatch decisions and generates grid-import alerts. These alerts are displayed on the live dashboard.

The dashboard retains the latest received alert, which may refer to an earlier simulation hour.

## Cloud Deployment

The project is deployed on Render using Docker.

- Deployment platform: Render
- Repository branch: main
- Root directory: agents
- Deployment environment: Docker
- Verified application commit: ddff468
- Deployment verified: 24 November 2026
- Cloud LLM provider: Groq
- MQTT broker: Eclipse Mosquitto
- Automation platform: Node-RED

Live dashboard:

https://multiagent-ai-system-6cri.onrender.com

## Automatic Failure Recovery

If the simulator does not receive a matching dispatch within 30 seconds, it raises a timeout error.

The process supervisor automatically restarts the simulator and creates a new simulation session.

Recovery was practically verified by temporarily pausing the coordinator and confirming that MQTT dispatch resumed after the simulator restarted.

## Limitations

- The current system uses synthetic data instead of physical IoT sensors.
- Energy management uses rule-based dispatch rather than a trained predictive model.
- Load shedding reduces electricity expenditure but leaves some flexible demand unserved.
- Equipment costs, initial stored-energy costs, battery degradation and export revenue are excluded from cost calculations.
- Battery SOC and simulation hour reset after simulator restart.
- Rolling dashboard history may temporarily include records from different simulation sessions after recovery.
- LLM-generated explanations may contain inaccuracies.
- Render free hosting may enter sleep mode during inactivity.
- The prototype is intended for educational simulation, not direct industrial electrical control.

## Future Scope

- Integration with physical IoT sensors and smart meters
- Machine learning-based demand forecasting
- Solar generation forecasting
- Persistent battery and simulation state
- Advanced multi-agent optimization
- Dynamic battery scheduling
- Database integration
- Mobile application integration
- Industrial microgrid applications

## AI Tools Disclosure

AI-assisted development tools, including Antigravity and ChatGPT, were used to support code generation, debugging, technical explanations and documentation.

The student participated in project configuration, integration, testing, troubleshooting, deployment and result verification.

## References

- Python: https://docs.python.org/3/
- MQTT: https://mqtt.org/
- Eclipse Mosquitto: https://mosquitto.org/
- Paho MQTT: https://eclipse.dev/paho/
- Groq: https://console.groq.com/docs
- Ollama: https://ollama.com/
- Node-RED: https://nodered.org/docs/
- Chart.js: https://www.chartjs.org/docs/
- Docker: https://docs.docker.com/
- GitHub: https://docs.github.com/
- Render: https://render.com/docs
- Pytest: https://docs.pytest.org/

## Conclusion

The project demonstrates an integrated multi-agent approach to simulated IoT energy management through MQTT communication, rule-based energy coordination, battery safety management, AI-generated explanations, automated alerts and cloud-based visualization.

The verified simulation results demonstrate the potential to reduce grid electricity expenditure while maintaining essential-load protection within the modeled operating conditions.
