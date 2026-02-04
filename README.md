# Model Registry

A centralized registry for managing, browsing, and serving machine learning models (Python and R).
This project provides:
- A Backend service for model and project management
- A REST API to interact with models and metadata
- A Web/Dashboard layer
- Utilities to load, register, and manage ML projects and artifacts

## Overview

- Purpose: centralize projects and models, provide prediction endpoints and a dashboard to manage artifacts.
- Primary languages: Python (app and dashboard) and R (supporting model artifacts and helper scripts under `model_registry/services/r`).
- Repo contains example projects under `projects/` and `model_registry/projects/`.

## Requirements

- Python 3.8+
- Poetry for dependency and environment management (recommended)
- Optional: R if you use the R model artifacts, Docker for containerized deployments

## Project Structure

```
model-registry/
├── model_registry/
│   ├── api/
│   │   ├── config/
│   │   ├── models/
│   │   ├── projects/
│   │   ├── routes/
│   │   ├── services/
│   │   ├── utils/
│   │   └── app_api.py
│   └── backend/
│       ├── assets/
│       ├── callbacks/
│       ├── components/
│       ├── config/
│       ├── data/
│       ├── layouts/
│       ├── models/
│       ├── pages/
│       ├── services/
│       └── app_backend.py
├── LICENSE
├── pyproject.toml
└── README.md
```

## Setup with Poetry

1. Install Poetry (if not installed):

```bash
# macOS / Linux
curl -sSL https://install.python-poetry.org | python3 -

# Windows (PowerShell)
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
```

2. Verify installation:

```bash
poetry install
```

3. Install dependencies and create the virtual environment:

```bash
poetry install
```

Notes:

- Project metadata and dependencies are defined in `pyproject.toml`.

## Running the application Poetry

The project is split into  **two main services** :

▶ Backend Service

Starts the core backend responsible for model and project management.

```bash
poetry run ml-repository-backend
```

Adjust the command as needed for your deployment (WSGI server, Docker, etc.).

▶ API Service

Starts the REST API layer

```bash
poetry run ml-repository-api
```
💡 Run each service in a separate terminal during development.

## Configure .env

To configure the project environment variables, rename the .env.example file to .env in both the api and backend directories.

## Quick Start (Docker)

The easiest way to run the Model Registry locally is using Docker Compose.

### Requirements
- Docker
- Docker Compose v2+

### Run

```bash

## Setup

Clone the repository with submodules:

```bash
git clone --recurse-submodules https://github.com/your-org/model-registry.git
cd model-registry
docker compose up --build
```

Open the following URLs in your browser:

Service  -	URL
- Backend (Dashboard)	http://localhost:8050
- API (REST)	http://localhost:8081

Health check

If the containers are running, you should see logs similar to:

- Backend running on port 8050

- API running on port 8081

## Contributing

- Follow existing code style and add tests for new features.
- Open an issue to discuss significant changes.

## License

See [LICENSE](LICENSE)

