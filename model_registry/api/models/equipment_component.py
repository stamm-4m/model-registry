"""Junction: which (sensor, actuator) pairs are mounted on a piece of
equipment (a bioreactor)."""
from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4
from model_registry.api.core.database import Base


class EquipmentComponent(Base):
    __tablename__ = "equipment_components"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    actuator_id = Column(UUID(as_uuid=True),
                         ForeignKey("actuators.id"), nullable=False)
    sensor_id = Column(UUID(as_uuid=True),
                       ForeignKey("sensors.id"), nullable=False)
    equipment_id = Column(UUID(as_uuid=True),
                          ForeignKey("equipments.id"), nullable=False)
