"""Junction between experiments and models."""
from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID

from model_registry.api.core.database import Base


class ExperimentModel(Base):
    __tablename__ = "experiment_models"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    experiment_id = Column(
        UUID(as_uuid=True), ForeignKey("experiments.id", ondelete="CASCADE"), nullable=True
    )
    model_id = Column(
        UUID(as_uuid=True), ForeignKey("models.id", ondelete="CASCADE"), nullable=True
    )
    role = Column(String, nullable=True, default="attached")
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
