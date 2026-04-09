from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from model_registry.api.core.database import Base

class LaboratoryProject(Base):
    __tablename__ = "laboratory_project"

    id = Column(UUID(as_uuid=True), primary_key=True)
    laboratory_id = Column(UUID(as_uuid=True), ForeignKey("laboratories.id"), nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)

    laboratory = relationship("Laboratory", back_populates="laboratory_projects")
    project = relationship("Project", back_populates="laboratory_projects")