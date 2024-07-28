FROM python:3.12-slim as base


RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    libmagic1=1:5.44-3 \
    wget=1.21.3-* \
    python3-dev \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
ENV PYTHONPATH=/app

COPY requirements.lock /app/requirements.lock

RUN pip install --no-cache-dir --upgrade pip==24.0 \
    && pip install --no-cache-dir -r requirements.lock

COPY src /app/src

# ============== local =============
FROM base as local
COPY requirements-dev.lock /app/requirements-dev.lock

RUN pip install --no-cache-dir --upgrade pip==24.0 \
    && pip install --no-cache-dir -r requirements-dev.lock
