"""
Junction between projects and models.

Same shape as ``project_soft_sensors`` but pointing at the new
``models`` table. A project can have multiple models attached, each
with a role label (primary / baseline / reference).
"""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID

from model_registry.api.core.database import Base


class ProjectModel(Base):
    __tablename__ = "project_models"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    project_id = Column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    model_id = Column(
        UUID(as_uuid=True), ForeignKey("models.id", ondelete="CASCADE"), nullable=False
    )
    role = Column(String, nullable=False, default="primary")
    created_at = Column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow
    )

    __table_args__ = (
        UniqueConstraint(
            "project_id", "model_id", "role", name="project_models_pmr_uq"
        ),
    )
