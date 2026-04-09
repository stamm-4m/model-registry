from uuid import uuid4
from sqlalchemy import Column, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from model_registry.api.core.database import Base
class Project(Base):
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    project_id = Column(String(255), nullable=False, unique=True)
    created_at = Column(String(255), nullable=False)

    laboratory_projects = relationship(
        "LaboratoryProject",
        back_populates="project"
    )