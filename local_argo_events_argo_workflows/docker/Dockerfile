FROM python:3.11-slim as base


RUN apt-get update \
    && apt-get install -y --no-install-recommends libgomp1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
ENV PYTHONPATH=/app


COPY requirements/app.txt /app/requirements/app.txt

RUN pip install --no-cache-dir --upgrade pip==24.0 \
    && pip install --no-cache-dir -r requirements/app.txt

COPY src/services /app/src/services
COPY src/workflows /app/src/workflows
COPY src/artifacts /app/src/artifacts
COPY src/schemas /app/src/schemas
COPY src/models /app/src/models
COPY src/utils /app/src/utils

# ============== local =============
FROM base as local
COPY requirements/dev.txt /app/requirements/dev.txt
RUN pip install --no-cache-dir -r requirements/dev.txt
