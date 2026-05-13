"""
Run-scoped time-series read endpoints.

The CRUD scaffold's ``GET /api/v1/sensor_readings/`` returns ALL rows
across the whole table; clients have to paginate-and-filter to find one
run's data. That doesn't scale: with N completed runs in the table, the
dashboard burns N pages just to find the live one.

This router adds three filtered endpoints — one per time-series table —
that filter in SQL by run_id. Single round-trip, indexed by the
hypertable's natural (time, run_id) primary key.

Endpoints:
    GET /api/v1/runs/{run_id}/sensor_readings
    GET /api/v1/runs/{run_id}/actuator_states
    GET /api/v1/runs/{run_id}/predictions

Common query params:
    since  ISO-8601 timestamp; only rows with time >= since (optional)
    limit  max rows to return (default 5000, capped at 50000)

Auth: requires ``model:view`` (same as the CRUD scaffold's read perms).
Added 2026-05-05 to remove the MAX_PAGES scaling cliff in
``services/timeseries.py``.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import asc
from sqlalchemy.orm import Session

from model_registry.api.core.database import get_db
from model_registry.api.core.dependencies import require_permission_resource
from model_registry.api.models.sensor_reading import SensorReading
from model_registry.api.models.actuator_state import ActuatorState
from model_registry.api.models.prediction import Prediction


router = APIRouter(prefix="/api/v1/runs", tags=["Run timeseries"])


# ---------------------------------------------------------- helpers

DEFAULT_LIMIT = 5000
MAX_LIMIT = 50000


def _row_to_dict(row) -> Dict[str, Any]:
    """Plain-dict serialisation that matches the CRUD scaffold's shape.

    SQLAlchemy ORM rows aren't directly JSON-able for UUID/datetime; we
    cast manually to keep the wire format predictable.
    """
    out: Dict[str, Any] = {}
    for col in row.__table__.columns:
        v = getattr(row, col.name)
        if isinstance(v, datetime):
            out[col.name] = v.isoformat()
        elif isinstance(v, UUID):
            out[col.name] = str(v)
        else:
            out[col.name] = v
    return out


def _parse_run_id(run_id: str) -> UUID:
    try:
        return UUID(run_id)
    except (ValueError, TypeError):
        raise HTTPException(400, f"invalid run_id UUID: {run_id!r}")


def _parse_since(since: Optional[str]) -> Optional[datetime]:
    if since is None or since == "":
        return None
    try:
        # tolerate trailing Z
        s = since[:-1] + "+00:00" if since.endswith("Z") else since
        return datetime.fromisoformat(s)
    except (ValueError, TypeError):
        raise HTTPException(400,
                             f"invalid since timestamp: {since!r} "
                             f"(expected ISO-8601)")


def _query(model, db: Session, run_id: UUID,
           since: Optional[datetime], limit: int) -> List[Dict[str, Any]]:
    """Build and execute the run-scoped time-series query."""
    q = db.query(model).filter(model.run_id == run_id)
    if since is not None:
        q = q.filter(model.time >= since)
    q = q.order_by(asc(model.time)).limit(limit)
    return [_row_to_dict(r) for r in q.all()]


# ---------------------------------------------------------- endpoints

@router.get("/{run_id}/sensor_readings",
            summary="Sensor readings for one run, optionally since a timestamp",
            response_model=List[Dict[str, Any]])
def get_sensor_readings(
    run_id: str,
    since: Optional[str] = Query(None,
                                  description="ISO-8601 lower bound on time"),
    limit: int = Query(DEFAULT_LIMIT, ge=1, le=MAX_LIMIT,
                        description=f"max rows (default {DEFAULT_LIMIT}, "
                                    f"max {MAX_LIMIT})"),
    db: Session = Depends(get_db),
    user=Depends(require_permission_resource("model:view", "Models")),
):
    """Return ``sensor_readings`` rows for this run, ordered by time ASC.

    Replaces the paginated CRUD scaffold for the live workspace chart.
    """
    return _query(SensorReading, db, _parse_run_id(run_id),
                  _parse_since(since), limit)


@router.get("/{run_id}/actuator_states",
            summary="Actuator states for one run, optionally since a timestamp",
            response_model=List[Dict[str, Any]])
def get_actuator_states(
    run_id: str,
    since: Optional[str] = Query(None,
                                  description="ISO-8601 lower bound on time"),
    limit: int = Query(DEFAULT_LIMIT, ge=1, le=MAX_LIMIT,
                        description=f"max rows (default {DEFAULT_LIMIT}, "
                                    f"max {MAX_LIMIT})"),
    db: Session = Depends(get_db),
    user=Depends(require_permission_resource("model:view", "Models")),
):
    """Return ``actuator_states`` rows for this run, ordered by time ASC."""
    return _query(ActuatorState, db, _parse_run_id(run_id),
                  _parse_since(since), limit)


@router.get("/{run_id}/predictions",
            summary="Predictions for one run, optionally since a timestamp",
            response_model=List[Dict[str, Any]])
def get_predictions(
    run_id: str,
    since: Optional[str] = Query(None,
                                  description="ISO-8601 lower bound on time"),
    limit: int = Query(DEFAULT_LIMIT, ge=1, le=MAX_LIMIT,
                        description=f"max rows (default {DEFAULT_LIMIT}, "
                                    f"max {MAX_LIMIT})"),
    db: Session = Depends(get_db),
    user=Depends(require_permission_resource("model:view", "Models")),
):
    """Return ``predictions`` rows for this run, ordered by time ASC."""
    return _query(Prediction, db, _parse_run_id(run_id),
                  _parse_since(since), limit)
