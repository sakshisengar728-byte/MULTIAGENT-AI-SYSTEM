#!/bin/sh
set -e

echo "Starting MQTT broker (Mosquitto)..."
mosquitto -c /app/mosquitto.conf &

echo "Waiting for the broker on port 1883..."
attempts=0
until python -c "import socket; socket.create_connection(('127.0.0.1', 1883), 2)" 2>/dev/null; do
  attempts=$((attempts + 1))
  if [ "$attempts" -ge 60 ]; then
    echo "Broker did not start. Check the logs above."
    exit 1
  fi
  sleep 0.5
done

echo "Broker is ready. Starting all services..."
exec python run_system.py