# HeyJarvis — Dockerfile
# Multi-stage build for production

# ---------------------------------------------------------------------------
# Base image
# ---------------------------------------------------------------------------
FROM python:3.11-slim AS base

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# ---------------------------------------------------------------------------
# Dependencies
# ---------------------------------------------------------------------------
FROM base AS deps

COPY pyproject.toml .
RUN pip install --no-cache-dir -e ".[dev]"

# ---------------------------------------------------------------------------
# Development image
# ---------------------------------------------------------------------------
FROM deps AS development

COPY . .

# Expose API and web ports
EXPOSE 8000 3000

CMD ["uvicorn", "apps.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# ---------------------------------------------------------------------------
# Production image
# ---------------------------------------------------------------------------
FROM deps AS production

# Run as non-root
RUN useradd --create-home appuser
USER appuser

EXPOSE 8000

CMD ["uvicorn", "apps.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
