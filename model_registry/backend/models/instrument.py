"""
Analytical instruments (HPLC, mass spec, NIR, off-gas analyzers, ...).
Distinct from sensors/actuators because they're often at-line / off-line.
"""

from uuid import uuid4

from sqlalchemy import Column, DateTime, String
from sqlalchemy.dialects.postgresql import ARRAY, UUID

from model_registry.api.core.database import Base


class Instrument(Base):
    __tablename__ = "instruments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    instrument_id = Column(String, nullable=False, unique=True)  # 'I-OG', 'I-MS', ...
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)  # 'HPLC' | 'mass_spec' | 'NIR' | ...
    mode = Column(String, nullable=False)  # 'online' | 'atline' | 'offline'
    measures = Column(ARRAY(String), nullable=True)
    typical_latency = Column(String, nullable=True)
    location = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=True)
