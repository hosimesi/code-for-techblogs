FROM python:3.12-slim as base


RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    libmagic1=1:5.44-3 \
    wget=1.21.3-* \
    && wget -qO/bin/grpc_health_probe https://github.com/grpc-ecosystem/grpc-health-probe/releases/download/v0.4.24/grpc_health_probe-linux-amd64 \
    && chmod +x /bin/grpc_health_probe \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
ENV PYTHONPATH=/app

COPY requirements.lock /app/requirements.lock

RUN pip install --no-cache-dir --upgrade pip==24.0 \
    && pip install --no-cache-dir -r requirements.lock

COPY pretrained_models /app/pretrained_models
COPY src/models /app/src/models
COPY src/proto /app/src/proto
COPY src/utils /app/src/utils
COPY src/services /app/src/services
COPY src/main.py /app/src/main.py

# ============== local =============
FROM base as local
COPY requirements-dev.lock /app/requirements-dev.lock

RUN pip install --no-cache-dir --upgrade pip==24.0 \
    && pip install --no-cache-dir -r requirements-dev.lock
