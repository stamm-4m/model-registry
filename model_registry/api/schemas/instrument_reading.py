"""Request schemas for MQTT instrument readings."""

from datetime import datetime, timezone
from typing import Annotated, Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class MQTTMeasurement(BaseModel):
    model_config = ConfigDict(extra="allow")

    measurement: str
    tags: dict[str, Any] = Field(default_factory=dict)
    fields: dict[str, Any]
    timestamp: float = Field(allow_inf_nan=False)

    @field_validator("timestamp")
    @classmethod
    def validate_timestamp(cls, value: float) -> float:
        try:
            datetime.fromtimestamp(value, tz=timezone.utc)
        except (OverflowError, OSError, ValueError) as exc:
            raise ValueError("timestamp must be a valid Unix timestamp") from exc
        return value


class MQTTInstrumentMessage(BaseModel):
    topic: str = Field(min_length=1)
    payload: Annotated[list[MQTTMeasurement], Field(min_length=1)] | MQTTMeasurement
    instrument_id: UUID | None = None
