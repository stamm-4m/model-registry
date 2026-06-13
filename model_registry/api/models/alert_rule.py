"""
Operator-defined per-experiment alert conditions.

Sources can be sensors, actuators, or model outputs. Conditions can be
threshold-based (gt/lt) or range-based (outside/inside).
"""
from sqlalchemy import Column, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4
from model_registry.api.core.database import Base


class AlertRule(Base):
    __tablename__ = "alert_rules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    experiment_id = Column(UUID(as_uuid=True),
                           ForeignKey("experiments.id"), nullable=False)
    name = Column(String, nullable=False)
    source_type = Column(String, nullable=False)   # 'sensor' | 'actuator' | 'model'
    source_id = Column(String, nullable=False)
    source_label = Column(String, nullable=False)
    condition = Column(String, nullable=False)     # 'gt' | 'lt' | 'outside' | 'inside'
    threshold = Column(Float, nullable=True)
    threshold_min = Column(Float, nullable=True)
    threshold_max = Column(Float, nullable=True)
    unit = Column(String, nullable=True)
    sustained_for_min = Column(Float, nullable=True)
    severity = Column(String, nullable=False, default="warning")
    enabled = Column(Boolean, nullable=False, default=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=True)
