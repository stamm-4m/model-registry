# Dash + Plotly App

Requisitos:

- Python 3.11+

Instalación local:

```bash
Option A — Entorno virtual con venv (alternativa antigua):

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

Option B — Usar Poetry (recomendado):

Poetry gestiona el entorno virtual y las dependencias vía `pyproject.toml`.

Instalar Poetry (recomendado vía instalador oficial):

```powershell
# Windows (PowerShell)
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
# Alternativamente, usar pipx: pipx install poetry
```

Instalar dependencias y crear el entorno:

```bash
poetry install
```

Activar el shell de Poetry (opcional) o ejecutar comandos directamente:

```bash
poetry shell          # entra en el entorno virtual manejado por Poetry
poetry run python -m model_registry.app   # ejecutar la app sin activar el shell
poetry run pytest     # ejecutar pruebas
```

Notas:

- `poetry.lock` y `pyproject.toml` deben mantenerse en el repositorio para reproducibilidad.
- Si migras desde `requirements.txt`, revisa las dependencias en `pyproject.toml`.

```

Docker:

```bash
docker build -t dash-app .
docker run -p 8050:8050 dash-app
```

Estructura destacada:

- `app/`: código principal (layout, callbacks, componentes)
- `assets/`: CSS, imágenes
- `data/`: datos de ejemplo
- `tests/`: pruebas

Siguientes pasos recomendados:

- Añadir pages y navegación
- Mover callbacks a módulos separados
- Integrar CI/CD y pruebas más completas
