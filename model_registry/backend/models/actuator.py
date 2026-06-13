"""Actuator catalog. Schema patched 2026-04-30 (Step 4) with the rich
fields FermOps' Actuator dataclass carries."""
from sqlalchemy import Column, String, DateTime, Float, Text
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4
from model_registry.api.core.database import Base


class Actuator(Base):
    __tablename__ = "actuators"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    actuator_id = Column(String, unique=True, nullable=True)  # 'A-FEED', 'A-IMP', ...
    name = Column(String, nullable=False)
    variable = Column(String, nullable=True)
    unit = Column(String, nullable=True)
    range_min = Column(Float, nullable=True)
    range_max = Column(Float, nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=True)
