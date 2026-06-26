"""
Junction: which instruments are attached to which bioreactor.
The bioreactor is identified via equipments.id.
"""

from uuid import uuid4

from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from model_registry.api.core.database import Base


class BioreactorInstrument(Base):
    __tablename__ = "bioreactor_instruments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    bioreactor_id = Column(
        UUID(as_uuid=True), ForeignKey("equipments.id"), nullable=False
    )
    instrument_id = Column(
        UUID(as_uuid=True), ForeignKey("instruments.id"), nullable=False
    )
