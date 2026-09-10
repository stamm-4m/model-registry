from uuid import uuid4

from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from model_registry.api.core.database import Base


class LaboratoryEquipment(Base):
    __tablename__ = "laboratory_equipments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    laboratory_id = Column(
        UUID(as_uuid=True), ForeignKey("laboratories.id"), nullable=False
    )
    equipment_id = Column(
        UUID(as_uuid=True), ForeignKey("equipments.id"), nullable=False
    )

    laboratory = relationship("Laboratory", back_populates="laboratory_equipments")
    equipment = relationship("Equipment", back_populates="laboratory_equipments")