"""
Operator notes attached to a specific phase of a specific run.
"""

from uuid import uuid4

from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID

from model_registry.api.core.database import Base


class PhaseNote(Base):
    __tablename__ = "phase_notes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    run_id = Column(UUID(as_uuid=True), ForeignKey("runs.id"), nullable=False)
    phase = Column(String, nullable=False)  # one of PHASE_TAXONOMY
    text = Column(Text, nullable=False)
    author_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, nullable=True)
