"""
Multi-parent lineage for federated aggregations.

Each row is one edge in the FL aggregation graph: "this aggregated
model was built from this contributor model at round N with weight W."
A FedAvg aggregation of N local models inserts N rows here.

Single-parent (retrain / fine-tune) lineage stays on
``models.parent_model_id``; this table is exclusively for FL multi-
parent links so the standard column gets read in the hot path.
"""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID

from model_registry.api.core.database import Base


class ModelContribution(Base):
    __tablename__ = "model_contributions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    aggregated_model_id = Column(
        UUID(as_uuid=True), ForeignKey("models.id", ondelete="CASCADE"), nullable=False
    )
    contributor_model_id = Column(
        UUID(as_uuid=True), ForeignKey("models.id"), nullable=False
    )
    federation_id = Column(
        UUID(as_uuid=True),
        ForeignKey("federations.id", ondelete="CASCADE"),
        nullable=False,
    )
    round_number = Column(Integer, nullable=False)

    # E.g. proportional to local dataset size in FedAvg.
    contribution_weight = Column(Numeric, nullable=False, default=1.0)

    # Per-contributor validation scores / loss etc.
    contribution_metrics = Column(JSONB, nullable=False, default=dict)

    created_at = Column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow
    )

    __table_args__ = (
        UniqueConstraint(
            "aggregated_model_id",
            "contributor_model_id",
            "round_number",
            name="model_contributions_acr_uq",
        ),
    )
