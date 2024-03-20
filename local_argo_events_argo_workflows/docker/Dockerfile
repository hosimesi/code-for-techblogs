FROM python:3.11-slim as base


RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
ENV PYTHONPATH=/app


COPY requirements/app.txt /app/requirements/app.txt

RUN pip install --no-cache-dir --upgrade pip==24.0 \
    && pip install --no-cache-dir -r requirements/app.txt

COPY src/schemas /app/src/schemas
COPY src/services /app/src/services
COPY src/workflows /app/src/workflows

# ============== local =============
FROM base as local
COPY requirements/dev.txt /app/requirements/dev.txt
RUN pip install --no-cache-dir -r requirements/dev.txt
