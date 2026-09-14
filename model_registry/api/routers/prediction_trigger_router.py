"""Trigger the workflow-orchestrator Airflow DAG for an experiment.

Centralizes the Airflow service-account credentials in the API layer so
callers (FermOps, the Dash backend, anything else) never need to hold
them directly — they only need permission to call this one endpoint.
Mirrors model_registry/backend/services/airflow_client.py (the Dash-side
trigger), but reachable over HTTP and the only place that actually knows
AIRFLOW_TRIGGER_USERNAME/PASSWORD.
"""

import logging
from datetime import datetime, timezone
from uuid import UUID

import requests
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from model_registry.api.config.settings import settings
from model_registry.api.core.database import get_db
from model_registry.api.core.dependencies import require_permission_resource
from model_registry.api.models.experiment import Experiment
from model_registry.api.models.experiment_soft_sensors import ExperimentSoftSensors
from model_registry.api.models.project import Project
from model_registry.api.models.run import Run
from model_registry.api.models.soft_sensors import SoftSensors

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["Prediction trigger"])

DAG_ID = "deployment_soft_sensors"


def _get_airflow_token() -> str | None:
    if not settings.AIRFLOW_API_BASE or not settings.AIRFLOW_TRIGGER_USERNAME:
        logger.warning(
            "[airflow] AIRFLOW_API_BASE/AIRFLOW_TRIGGER_USERNAME not configured — skipping trigger."
        )
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


@router.post("/experiments/{experiment_id}/trigger-prediction")
def trigger_prediction(
    experiment_id: UUID,
    db: Session = Depends(get_db),
    user=Depends(require_permission_resource("experiments:write", "Experiments")),
):
    """Create the experiment's next run and start the Airflow prediction
    loop for it (deployment_soft_sensors).

    Resolves the models attached via experiment_soft_sensors (to their
    models.slug) and the experiment's vessel_id, and passes both in the
    DAG trigger conf — same contract documented in
    workflow-orchestrator/docs/trigger-from-model-registry.md.

    Best-effort on the Airflow side: a failed/unconfigured trigger doesn't
    raise, the run is still created either way — callers should check the
    "triggered" field in the response.
    """
    exp = db.get(Experiment, experiment_id)
    if exp is None:
        raise HTTPException(404, f"Experiment {experiment_id} not found")

    project = db.get(Project, exp.project_id) if exp.project_id else None
    project_name = project.name if project else ""

    links = (
        db.query(ExperimentSoftSensors)
        .filter(ExperimentSoftSensors.experiment_id == exp.id)
        .all()
    )
    model_ids: list[str] = []
    for link in links:
        if not link.soft_sensor_id:
            continue
        ss = db.get(SoftSensors, link.soft_sensor_id)
        if ss and ss.slug:
            model_ids.append(ss.slug)

    run = Run(experiment_id=exp.id, start_time=datetime.now(timezone.utc))
    db.add(run)
    db.commit()
    db.refresh(run)

    token = _get_airflow_token()
    if not token:
        return {
            "triggered": False,
            "run_id": str(run.id),
            "model_ids": model_ids,
            "reason": "Airflow not configured or unreachable",
        }

    conf = {
        "run_id": str(run.id),
        "experiment_id": str(exp.id),
        "project_id": str(exp.project_id),
        "project_name": project_name,
    }
    if model_ids:
        conf["model_ids"] = model_ids
    if exp.vessel_id:
        conf["vessel_id"] = str(exp.vessel_id)

    try:
        resp = requests.post(
            f"{settings.AIRFLOW_API_BASE.rstrip('/')}/api/v2/dags/{DAG_ID}/dagRuns",
            headers={"Authorization": f"Bearer {token}"},
            json={"logical_date": None, "conf": conf},
            timeout=10,
        )
        triggered = resp.status_code in (200, 201)
        if not triggered:
            logger.error(f"[airflow] trigger failed: HTTP {resp.status_code} {resp.text}")
        return {"triggered": triggered, "run_id": str(run.id), "model_ids": model_ids}
    except Exception as exc:
        logger.error(f"[airflow] trigger request failed: {exc}")
        return {
            "triggered": False,
            "run_id": str(run.id),
            "model_ids": model_ids,
            "reason": str(exc),
        }
