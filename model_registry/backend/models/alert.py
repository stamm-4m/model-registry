"""A triggered alert (a fired rule). Note: alert_rules holds the
*conditions*; alerts holds the *firings*."""
from sqlalchemy import Column, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4
from model_registry.api.core.database import Base


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    condition = Column(Text, nullable=True)
    message = Column(Text, nullable=True)
    experiment_id = Column(UUID(as_uuid=True),
                           ForeignKey("experiments.id"), nullable=False)
