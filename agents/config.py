import os

# ---------- MQTT broker ----------
BROKER_HOST = "127.0.0.1"
BROKER_PORT = 1883

# ---------- MQTT topics ----------
TELEMETRY_TOPIC = "energy/sensors/telemetry"
PROPOSAL_PREFIX = "energy/proposals/"
DECISION_TOPIC = "energy/coordinator/decision"
EXPLANATION_TOPIC = "energy/llm/explanation"
ALERT_TOPIC = "energy/alerts/grid"

# ---------- Tariff (Rs per kWh) ----------
PEAK_PRICE = 8.0           # applies to hours 17 to 21
OFFPEAK_PRICE = 4.0

# ---------- Loads and battery ----------
ESSENTIAL_LOAD_KW = 1.2    # never shed
MIN_SOC = 20.0             # percent
MAX_SOC = 90.0             # percent
MAX_BATTERY_KW = 2.5       # charge and discharge limit
BATTERY_CAPACITY_KWH = 10.0
CHARGE_EFFICIENCY = 0.95

# ---------- Local LLM (Ollama) ----------
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
OLLAMA_MODEL = "llama3.2:3b"

# ---------- Dashboard ----------
# On a laptop: 127.0.0.1 and port 8050.
# On Render: the Dockerfile sets DASHBOARD_HOST=0.0.0.0, and Render provides PORT.
DASHBOARD_HOST = os.environ.get("DASHBOARD_HOST", "127.0.0.1")
DASHBOARD_PORT = int(os.environ.get("PORT", "8050"))

# ---------- Cloud LLM (Groq) ----------
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.1-8b-instant")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
LLM_INTERVAL = 30
