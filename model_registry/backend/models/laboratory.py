import uuid

from sqlalchemy import Column, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from model_registry.api.core.database import Base


class Laboratory(Base):
    __tablename__ = "laboratories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text, nullable=False)
    location = Column(Text)

    laboratory_projects = relationship("LaboratoryProject", back_populates="laboratory")
