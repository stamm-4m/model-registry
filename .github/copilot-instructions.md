# Copilot Instructions for model-registry

## Build, Test, and Lint Commands

- **Install dependencies:**
  - `poetry install`
- **Run backend service:**
  - `poetry run ml-repository-backend` (or `python model_registry/backend/app_backend.py`)
- **Run API service:**
  - `poetry run ml-repository-api` (or `uvicorn model_registry.api.app_api:api --host 0.0.0.0 --port 8080`)
- **Run all services with Docker Compose:**
  - `docker compose up --build`
- **Run a single test:**
  - `pytest tests/test_app.py -k <test_name>`
- **Run all tests:**
  - `pytest`
- **Lint code:**
  - `poetry run ruff .` or `poetry run flake8 .`

## High-Level Architecture

- **Backend (Dash/Flask):**
  - Located in `model_registry/backend/`, provides the dashboard UI and manages projects/models.
- **API (FastAPI):**
  - Located in `model_registry/api/`, exposes REST endpoints for model registration, metadata, and predictions.
- **R Model Service:**
  - Located in `model_registry/api/services/r/`, serves R-based ML models via Plumber. Integrated via Docker Compose as `r-api`.
- **Metadata Tools:**
  - `model_registry/backend/vendor/metadata_tools/` provides utilities for FAIR Data Station and FAIRDOM-SEEK metadata management.
- **Docker Compose:**
  - Orchestrates backend, API, and R services for local development.

## Key Conventions

- **Environment Variables:**
  - Copy `.env.example` to `.env` in both `api/` and `backend/` before running locally.
- **Model Metadata:**
  - YAML files for model metadata are stored in `configs/` or project-specific `projects/<project_id>/configs/`.
- **Model Files:**
  - Trained models are stored in `projects/<project_id>/models/`.
- **R API Integration:**
  - Python API forwards prediction requests to the R service if the model is R-based.
- **Testing:**
  - Minimal test example in `tests/test_app.py`. Add more tests for new features.
- **Poetry Scripts:**
  - Use `poetry run ml-repository-backend` and `poetry run ml-repository-api` for local dev.
- **Linting:**
  - Use Ruff and Flake8. Black is used for formatting (see pyproject.toml).

---

This file summarizes build/test/lint commands, architecture, and conventions for Copilot and future contributors. Would you like to adjust anything or add coverage for additional areas (e.g., advanced deployment, CI/CD, or more on metadata tools)?
