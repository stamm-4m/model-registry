"""Persisted MQTT measurements from external instruments."""

from uuid import uuid4

from sqlalchemy import Column, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from model_registry.api.core.database import Base


class InstrumentReading(Base):
    __tablename__ = "instrument_readings"
    __table_args__ = (Index("idx_instrument_readings_time", "time"),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    instrument_id = Column(
        UUID(as_uuid=True),
        ForeignKey("instruments.id", ondelete="SET NULL"),
        nullable=True,
    )
    topic = Column(Text, nullable=False)
    measurement = Column(String, nullable=False)
    time = Column(DateTime(timezone=True), nullable=False)
    payload = Column(JSONB, nullable=False)
    received_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    instrument = relationship("Instrument", back_populates="readings")
