"""Sensor catalog. Schema patched 2026-04-30 (Step 4) with the rich
fields FermOps' Sensor dataclass carries (sensor_id text, variable,
range_min/max, accuracy, mode)."""
from sqlalchemy import Column, String, DateTime, Float, Text
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4
from model_registry.api.core.database import Base


class Sensor(Base):
    __tablename__ = "sensors"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    sensor_id = Column(String, unique=True, nullable=True)   # 'S-DO', 'S-pH', ...
    name = Column(String, nullable=False)
    variable = Column(String, nullable=True)                 # 'DO', 'pH', 'Temperature', ...
    unit = Column(String, nullable=True)
    range_min = Column(Float, nullable=True)
    range_max = Column(Float, nullable=True)
    accuracy = Column(String, nullable=True)
    mode = Column(String, nullable=True, default="online")
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=True)
