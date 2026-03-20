FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

# Copy dependency definitions
COPY pyproject.toml poetry.lock* ./

# Install Python dependencies (no venv inside container)
RUN poetry config virtualenvs.create false \
    && poetry install --without dev --no-interaction --no-root

# Copy source code
COPY model_registry ./model_registry
COPY README.md LICENSE ./

EXPOSE 8000
