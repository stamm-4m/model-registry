from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
import uuid
from model_registry.api.core.database import Base

class ProjectSoftSensor(Base):
    __tablename__ = "project_soft_sensors"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    soft_sensor_id = Column(UUID(as_uuid=True), ForeignKey("soft_sensors.id"), nullable=False)
