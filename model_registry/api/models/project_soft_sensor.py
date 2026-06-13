"""
Junction between projects and soft_sensors.

Schema reminder:
    project_soft_sensors(id uuid PK, project_id uuid FK, soft_sensor_id uuid FK)
"""
from uuid import uuid4
from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from model_registry.api.core.database import Base


class ProjectSoftSensor(Base):
    __tablename__ = "project_soft_sensors"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    project_id = Column(UUID(as_uuid=True),
                         ForeignKey("projects.id"),
                         nullable=False)
    soft_sensor_id = Column(UUID(as_uuid=True),
                             ForeignKey("soft_sensors.id"),
                             nullable=False)
