"""Experiment design — schema patched 2026-04-30 (Step 4) with the rich
fields FermOps' Experiment dataclass carries (mode, scale, organism,
lead, status, is_reference, tags, vessel_id, lab_id, final_titer)."""

from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID

from model_registry.api.core.database import Base


class Experiment(Base):
    __tablename__ = "experiments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    experiment_id = Column(String, unique=True, nullable=True)  # 'B-2026-127'
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    lab_id = Column(UUID(as_uuid=True), ForeignKey("laboratories.id"), nullable=True)
    vessel_id = Column(UUID(as_uuid=True), ForeignKey("equipments.id"), nullable=True)
    name = Column(String, nullable=False)  # 'feed step-up trial'
    description = Column(Text, nullable=True)
    lead = Column(String, nullable=True)  # 'A. Patel'
    status = Column(String, nullable=True, default="running")
    mode = Column(String, nullable=True)  # 'fed-batch'
    scale = Column(String, nullable=True)  # '50L'
    organism = Column(String, nullable=True)
    medium = Column(String, nullable=True)
    is_reference = Column(Boolean, nullable=True, default=False)
    final_titer = Column(Float, nullable=True)
    tags = Column(ARRAY(String), nullable=True)
    initial_conditions = Column(JSONB, nullable=True)
    set_points = Column(JSONB, nullable=True)
    start_time = Column(DateTime(timezone=True), nullable=True)
    end_time = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime, nullable=True)
