FROM python:3.13-slim

# The Mosquitto MQTT broker runs inside the same container
RUN apt-get update \
    && apt-get install -y --no-install-recommends mosquitto \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1 \
    DASHBOARD_HOST=0.0.0.0

CMD ["sh", "start.sh"]