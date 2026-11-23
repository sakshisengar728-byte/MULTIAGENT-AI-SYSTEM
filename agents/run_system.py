import os
import signal
import subprocess
import sys
import time

SERVICES = [
    "load_agent",
    "generation_agent",
    "storage_agent",
    "pricing_agent",
    "coordinator",
    "llm_explainer",
    "dashboard",
]
SIMULATOR = "mqtt_simulator"

# On Windows, a separate process group stops Ctrl+C from killing children early
FLAGS = subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0


def start(module):
    return subprocess.Popen([sys.executable, "-m", module], creationflags=FLAGS)


def on_sigterm(signum, frame):
    # Render sends SIGTERM when it stops the container. Treat it like Ctrl+C.
    raise KeyboardInterrupt


signal.signal(signal.SIGTERM, on_sigterm)

procs = {}
try:
    for module in SERVICES:
        procs[module] = start(module)
    time.sleep(3)                       # let every subscriber connect first
    procs[SIMULATOR] = start(SIMULATOR)
    print("All components started. Open the dashboard in your browser.", flush=True)
    print("Press Ctrl+C to stop everything.", flush=True)

    while True:
        time.sleep(2)
        for module in list(procs):
            if procs[module].poll() is not None:        # a service crashed
                print(f"[RUN_SYSTEM] {module} stopped. Restarting it.", flush=True)
                procs[module] = start(module)
except KeyboardInterrupt:
    print("\nStopping all components...", flush=True)
finally:
    for proc in procs.values():
        proc.terminate()
    print("All components stopped.", flush=True)