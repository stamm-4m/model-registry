"""
Per-run overrides of default phase boundaries.
"""
from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4
from model_registry.api.core.database import Base


class PhaseOverride(Base):
    __tablename__ = "phase_overrides"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    run_id = Column(UUID(as_uuid=True), ForeignKey("runs.id"), nullable=False)
    phase = Column(String, nullable=False)
    start_h = Column(Float, nullable=True)
    end_h = Column(Float, nullable=True)
    set_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"),
                            nullable=True)
    set_at = Column(DateTime, nullable=True)
