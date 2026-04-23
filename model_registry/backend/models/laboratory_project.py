import uuid
from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from model_registry.api.core.database import Base


class LaboratoryProject(Base):
    __tablename__ = "laboratory_project"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    laboratory_id = Column(UUID(as_uuid=True), ForeignKey("laboratories.id"), primary_key=True)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), primary_key=True)