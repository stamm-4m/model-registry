"""MQTT ingestion and dashboard query endpoints for instrument readings."""

from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from model_registry.api.core.database import get_db
from model_registry.api.core.dependencies import require_permission_resource
from model_registry.api.models.instrument_reading import InstrumentReading
from model_registry.api.schemas.instrument_reading import (
    MQTTInstrumentMessage,
    MQTTMeasurement,
)

router = APIRouter(prefix="/api/v1/instrument_readings", tags=["Instrument readings"])


def _serialize_reading(row: InstrumentReading) -> dict[str, Any]:
    return {
        "id": str(row.id),
        "instrument_id": str(row.instrument_id) if row.instrument_id else None,
        "topic": row.topic,
        "measurement": row.measurement,
        "time": row.time.isoformat(),
        "payload": row.payload,
        "received_at": row.received_at.isoformat() if row.received_at else None,
    }


def _measurement_row(
    topic: str, instrument_id: UUID | None, item: MQTTMeasurement
) -> InstrumentReading:
    payload = item.model_dump(mode="json")
    return InstrumentReading(
        instrument_id=instrument_id,
        topic=topic,
        measurement=item.measurement,
        time=datetime.fromtimestamp(item.timestamp, tz=timezone.utc),
        payload=payload,
    )


@router.post("/mqtt", status_code=201)
def ingest_mqtt_message(
    message: MQTTInstrumentMessage,
    db: Session = Depends(get_db),
    user=Depends(
        require_permission_resource("instrument_readings:write", "instrument_readings")
    ),
):
    """Persist each measurement in an MQTT message as a separate reading."""
    items = message.payload if isinstance(message.payload, list) else [message.payload]
    rows = [
        _measurement_row(message.topic, message.instrument_id, item) for item in items
    ]
    db.add_all(rows)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            409, "instrument_id does not reference an existing instrument"
        ) from exc
    for row in rows:
        db.refresh(row)
    return {"inserted": len(rows), "readings": [_serialize_reading(row) for row in rows]}


@router.get("/recent", response_model=list[dict[str, Any]])
def get_recent_instrument_readings(
    offset: int = Query(0, ge=0),
    limit: int = Query(5000, ge=1, le=50000),
    topic: str | None = None,
    measurement: str | None = None,
    since: datetime | None = None,
    until: datetime | None = None,
    db: Session = Depends(get_db),
    user=Depends(
        require_permission_resource("instrument_readings:read", "instrument_readings")
    ),
):
    """Return readings newest-first, with optional filters for dashboard use."""
    if since is not None and until is not None and since > until:
        raise HTTPException(422, "since must be earlier than or equal to until")
    if since is not None and since.tzinfo is None:
        since = since.replace(tzinfo=timezone.utc)
    if until is not None and until.tzinfo is None:
        until = until.replace(tzinfo=timezone.utc)

    query = db.query(InstrumentReading)
    if topic is not None:
        query = query.filter(InstrumentReading.topic == topic)
    if measurement is not None:
        query = query.filter(InstrumentReading.measurement == measurement)
    if since is not None:
        query = query.filter(InstrumentReading.time >= since)
    if until is not None:
        query = query.filter(InstrumentReading.time <= until)
    rows = (
        query.order_by(InstrumentReading.time.desc(), InstrumentReading.id.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return [_serialize_reading(row) for row in rows]
