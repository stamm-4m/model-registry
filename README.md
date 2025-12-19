# Model Registry

A central registry for managing, browsing, and serving machine learning models (Python and R). This repository provides a REST API, a web dashboard, and utilities to load and manage project/model metadata.

## Overview

- Purpose: centralize projects and models, provide prediction endpoints and a dashboard to manage artifacts.
- Primary languages: Python (app and dashboard) and R (supporting model artifacts and helper scripts under `model_registry/services/r`).
- Repo contains example projects under `projects/` and `model_registry/projects/`.

## Requirements

- Python 3.8+
- Poetry for dependency and environment management (recommended)
- Optional: R if you use the R model artifacts, Docker for containerized deployments

## Setup with Poetry

1. Install Poetry (if not installed):

```bash
# macOS / Linux
curl -sSL https://install.python-poetry.org | python3 -

# Windows (PowerShell)
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
```

2. Install dependencies and create the virtual environment:

```bash
poetry install
```

3. Activate the virtual environment (optional):

```bash
poetry shell
```

4. Run commands inside Poetry environment without shell:

```bash
poetry run python model_registry/app.py
```

Notes:

- Project metadata and dependencies are defined in `pyproject.toml`.
- If you prefer a global venv, you can use `poetry export` to generate a requirements file.

## Running the application

- Entry point: `model_registry/app.py` — this starts the API/dashboard depending on project configuration.

Example (Poetry):

```bash
poetry run python model_registry/app.py
```

Adjust the command as needed for your deployment (WSGI server, Docker, etc.).

## Tests

- Example tests are in `tests/test_app.py`.

Run tests with Poetry:

```bash
poetry run pytest -q
```

## Adding a project or model

1. Add your project folder under `projects/<ProjectName>/` with a `project_info.yaml` file.
2. Put model artifacts in `projects/<ProjectName>/models/` and configuration files under `configs/`.
3. Use `model_registry/utils/project_loader.py` to load project metadata programmatically.

## Packaging & deployment suggestions

- Local dev: use `poetry run` commands or `poetry shell`.
- Production: serve via a WSGI server (Gunicorn/uvicorn) or containerize with Docker.

Example minimal Dockerfile guidance:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml poetry.lock* /app/
RUN pip install poetry && poetry config virtualenvs.create false && poetry install --no-dev --no-interaction
COPY . /app
CMD ["poetry", "run", "python", "model_registry/app.py"]
```

## Useful files and locations

- `model_registry/app.py` — main entry point
- `model_registry/utils/project_loader.py` — helper to load projects
- `model_registry/services/r/` — R scripts and instructions for R-based models
- `pyproject.toml` — dependency and package configuration

## Contributing

- Follow existing code style and add tests for new features.
- Open an issue to discuss significant changes.

## License

See [LICENSE](LICENSE)

---

If you want, I can also:

- Add a `Dockerfile` and `docker-compose.yml` for local testing
- Export a `requirements.txt` from Poetry (`poetry export -f requirements.txt`) for non-Poetry environments
- Add CI steps (GitHub Actions) to run tests and linting

Tell me which of the above you'd like next.
