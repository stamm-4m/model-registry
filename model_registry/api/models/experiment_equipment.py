"""Junction: which equipments (bioreactors) does an experiment use?"""
from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4
from model_registry.api.core.database import Base


class ExperimentEquipment(Base):
    __tablename__ = "experiments_equipments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    experiment_id = Column(UUID(as_uuid=True),
                           ForeignKey("experiments.id"), nullable=False)
    equipment_id = Column(UUID(as_uuid=True),
                          ForeignKey("equipments.id"), nullable=False)
