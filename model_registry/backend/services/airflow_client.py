"""Trigger the workflow-orchestrator Airflow DAG when an experiment starts.

Called right after an experiment and its first run are created, so the
soft-sensor prediction loop (deployment_soft_sensors) starts automatically
instead of needing someone to trigger it by hand. Contract documented in
workflow-orchestrator/docs/trigger-from-model-registry.md.

Never raises — a failure here should not block experiment creation in the
UI; it's logged and surfaced as a return value instead.
"""

import logging

import requests

from model_registry.backend.config.settings import settings

logger = logging.getLogger(__name__)

DAG_ID = "deployment_soft_sensors"


def _get_token() -> str | None:
    if not settings.AIRFLOW_API_BASE or not settings.AIRFLOW_TRIGGER_USERNAME:
        logger.warning("[airflow] AIRFLOW_API_BASE/AIRFLOW_TRIGGER_USERNAME not configured — skipping trigger.")
        return None
    try:
        resp = requests.post(
            f"{settings.AIRFLOW_API_BASE.rstrip('/')}/auth/token",
            json={
                "username": settings.AIRFLOW_TRIGGER_USERNAME,
                "password": settings.AIRFLOW_TRIGGER_PASSWORD,
            },
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()["access_token"]
    except Exception as exc:
        logger.error(f"[airflow] failed to obtain token: {exc}")
        return None


def trigger_deployment_soft_sensors(
    run_id: str,
    experiment_id: str,
    project_id: str,
    project_name: str,
    model_ids: list[str] | None = None,
    vessel_id: str | None = None,
    user_id: str | None = None,
) -> bool:
    """POST a new dagRun for deployment_soft_sensors. Returns True on success.

    model_ids is the list of models.slug for every model attached to this
    experiment (see _start_prediction_loop) — Airflow runs a prediction for
    each one, instead of its own env-var pin, when present. vessel_id is the
    bioreactor this experiment runs on (experiments.vessel_id), passed
    through for provenance.
    """
    token = _get_token()
    if not token:
        return False

    conf = {
        "run_id": run_id,
        "experiment_id": experiment_id,
        "project_id": project_id,
        "project_name": project_name,
    }
    if model_ids:
        conf["model_ids"] = model_ids
    if vessel_id:
        conf["vessel_id"] = vessel_id
    if user_id:
        conf["user_id"] = user_id

    try:
        resp = requests.post(
            f"{settings.AIRFLOW_API_BASE.rstrip('/')}/api/v2/dags/{DAG_ID}/dagRuns",
            headers={"Authorization": f"Bearer {token}"},
            json={"logical_date": None, "conf": conf},
            timeout=10,
        )
        if resp.status_code not in (200, 201):
            logger.error(f"[airflow] trigger failed: HTTP {resp.status_code} {resp.text}")
            return False
        logger.info(f"[airflow] triggered {DAG_ID} for run_id={run_id}")
        return True
    except Exception as exc:
        logger.error(f"[airflow] trigger request failed: {exc}")
        return False
