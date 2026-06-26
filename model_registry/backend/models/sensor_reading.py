"""Time-series sensor measurements. TimescaleDB hypertable; composite PK."""

from sqlalchemy import Column, DateTime, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from model_registry.api.core.database import Base


class SensorReading(Base):
    __tablename__ = "sensor_readings"

    time = Column("time", DateTime(timezone=True), primary_key=True)
    run_id = Column(
        UUID(as_uuid=True), ForeignKey("runs.id"), primary_key=True, nullable=False
    )
    sensor_id = Column(
        UUID(as_uuid=True), ForeignKey("sensors.id"), primary_key=True, nullable=False
    )
    value = Column(Float, nullable=True)
