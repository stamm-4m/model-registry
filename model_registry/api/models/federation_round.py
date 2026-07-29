"""Per-round summary of a federation aggregation round.

One row = one aggregation round of a federation: the resulting global-model
metric, how many participants were expected/received, and the per-participant
contribution weights (JSONB {project_id: weight}). Drives the convergence and
contribution charts. See [[project_fl_rl_views]].
"""
from datetime import datetime
from uuid import uuid4

from sqlalchemy import (Column, DateTime, ForeignKey, Integer, Numeric, String,
                        UniqueConstraint)
from sqlalchemy.dialects.postgresql import JSONB, UUID

from model_registry.api.core.database import Base


class FederationRound(Base):
    __tablename__ = "federation_rounds"
    __table_args__ = (UniqueConstraint("federation_id", "round_number",
                                       name="federation_rounds_uq"),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    federation_id = Column(UUID(as_uuid=True),
                           ForeignKey("federations.id", ondelete="CASCADE"), nullable=False)
    round_number = Column(Integer, nullable=False)
    status = Column(String, nullable=False, default="completed")
    global_metric_name = Column(String)
    global_metric_value = Column(Numeric)
    participants_expected = Column(Integer)
    participants_received = Column(Integer)
    contributions = Column(JSONB, nullable=False, default=dict)
    global_model_id = Column(UUID(as_uuid=True), ForeignKey("models.id"))
    started_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    aggregated_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
