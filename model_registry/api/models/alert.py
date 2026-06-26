"""A triggered alert (a fired rule). Note: alert_rules holds the
*conditions*; alerts holds the *firings*."""

from uuid import uuid4

from sqlalchemy import Column, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID

from model_registry.api.core.database import Base


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    condition = Column(Text, nullable=True)
    message = Column(Text, nullable=True)
    experiment_id = Column(
        UUID(as_uuid=True), ForeignKey("experiments.id"), nullable=False
    )
    # Enriched display fields (08_alerts_enrich.sql). NULL on legacy rows;
    # FermOps falls back to per-field defaults.
    created_at = Column(DateTime, nullable=True)
    alert_type = Column(Text, nullable=True)  # 'Drift' | 'Divergence' | ...
    variable = Column(Text, nullable=True)
    phase = Column(Text, nullable=True)
    status = Column(Text, nullable=False, server_default="active")
