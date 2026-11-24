#!/bin/sh
set -e

echo "Starting MQTT broker..."
mosquitto -c /app/mosquitto.conf &

echo "Waiting for MQTT broker..."
attempts=0

until python -c "import socket; socket.create_connection(('127.0.0.1', 1883), 2)" 2>/dev/null; do
    attempts=$((attempts + 1))
    if [ "$attempts" -ge 60 ]; then
        echo "MQTT broker failed to start"
        exit 1
    fi
    sleep 0.5
done

echo "MQTT broker is ready."

echo "Starting Node-RED..."
/app/node-red/node_modules/.bin/node-red \
    --userDir /app/node-red \
    --settings /app/node-red/settings.js \
    /app/node-red/flows.json &

echo "Waiting for Node-RED..."
attempts=0

until python -c "import socket; socket.create_connection(('127.0.0.1', 1880), 2)" 2>/dev/null; do
    attempts=$((attempts + 1))
    if [ "$attempts" -ge 60 ]; then
        echo "Node-RED failed to start"
        exit 1
    fi
    sleep 0.5
done

echo "Starting Python agents..."
exec python run_system.py
