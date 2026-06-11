from uuid import uuid4
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from model_registry.api.core.database import Base
class Project(Base):
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    project_id = Column(String(255), nullable=False, unique=True)
    created_at = Column(String(255), nullable=False)

    # Added 2026-05-22 (compat patch section 9.1). The DB ALTER TABLE
    # ran on first init; declaring them here so the CRUD scaffold
    # returns them on GET / accepts them on POST/PATCH.
    # lead_user_id is the project's PI -- FK to users.id (changed from
    # free text the same day).
    objective    = Column(Text, nullable=True)
    lead_user_id = Column(UUID(as_uuid=True),
                           ForeignKey("users.id"),
                           nullable=True)
    status       = Column(String(32), nullable=False, server_default="active")
    tags         = Column(ARRAY(String), nullable=False, server_default="{}")
    started_at   = Column(DateTime(timezone=True), nullable=True)
    closed_at    = Column(DateTime(timezone=True), nullable=True)
    updated_at   = Column(DateTime(timezone=True), nullable=True)

    laboratory_projects = relationship(
        "LaboratoryProject",
        back_populates="project"
    )
    #experiments = relationship(
    #    "Experiment",
    #    back_populates="project",
    #    cascade="all, delete-orphan"
    #)