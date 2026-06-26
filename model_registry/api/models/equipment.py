"""Equipments (bioreactors are the canonical instance: brand+model+version)."""

from uuid import uuid4

from sqlalchemy import Column, DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID

from model_registry.api.core.database import Base


class Equipment(Base):
    __tablename__ = "equipments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    brand = Column(String, nullable=True)
    model = Column(String, nullable=True)
    version = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=True)
