"""
Junction between projects and soft sensors.

Maps projects to the enriched ``soft_sensors`` table. A project can have
multiple soft sensors attached, each with a role label.
"""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID

from model_registry.api.core.database import Base


class ProjectSoftSensors(Base):
    __tablename__ = "project_soft_sensors"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    project_id = Column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    soft_sensor_id = Column(
        UUID(as_uuid=True),
        ForeignKey("soft_sensors.id", ondelete="CASCADE"),
        nullable=False,
    )
    role = Column(String, nullable=False, default="primary")
    created_at = Column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow
    )

    __table_args__ = (
        UniqueConstraint(
            "project_id", "soft_sensor_id", "role", name="project_soft_sensors_pmr_uq"
        ),
    )