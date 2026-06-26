"""Time-series actuator states. TimescaleDB hypertable; composite PK."""

from sqlalchemy import Column, DateTime, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from model_registry.api.core.database import Base


class ActuatorState(Base):
    __tablename__ = "actuator_states"

    time = Column("time", DateTime(timezone=True), primary_key=True)
    run_id = Column(
        UUID(as_uuid=True), ForeignKey("runs.id"), primary_key=True, nullable=False
    )
    actuator_id = Column(
        UUID(as_uuid=True), ForeignKey("actuators.id"), primary_key=True, nullable=False
    )
    value = Column(Float, nullable=True)
