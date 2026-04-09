from sqlalchemy import Column, String, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from model_registry.api.core.database import Base

class Laboratory(Base):
    __tablename__ = "laboratories"

    id = Column(UUID(as_uuid=True), primary_key=True)
    name = Column(String(255), nullable=False)
    location = Column(String(255), nullable=False)

    laboratory_projects = relationship(
        "LaboratoryProject",
        back_populates="laboratory"
    )