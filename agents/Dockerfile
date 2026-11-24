FROM node:24-bookworm-slim AS node_runtime

FROM python:3.13-slim-bookworm

COPY --from=node_runtime /usr/local/bin/node /usr/local/bin/node
COPY --from=node_runtime /usr/local/lib/node_modules/npm /usr/local/lib/node_modules/npm

RUN ln -s /usr/local/lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm

RUN apt-get update \
    && apt-get install -y --no-install-recommends mosquitto libstdc++6 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY node-red/package.json node-red/package-lock.json /app/node-red/
RUN cd /app/node-red && npm ci --omit=dev

COPY . .

ENV PYTHONUNBUFFERED=1 \
    DASHBOARD_HOST=0.0.0.0

CMD ["sh", "start.sh"]
