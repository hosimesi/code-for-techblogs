FROM python:3.13-slim AS base

RUN apt-get update && apt-get install -y \
    gcc \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
COPY . /app

RUN uv sync --group=app --group=dev --frozen --no-cache

EXPOSE 8000
