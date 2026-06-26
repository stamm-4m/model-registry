"""
Membership of a project in a federation.

A project participates in one or more federations, each with a role
(coordinator vs participant). Local-dataset stats per participant help
weighted aggregation strategies (FedAvg weights by data volume, etc.).
"""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID

from model_registry.api.core.database import Base


class FederationParticipant(Base):
    __tablename__ = "federation_participants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    federation_id = Column(
        UUID(as_uuid=True),
        ForeignKey("federations.id", ondelete="CASCADE"),
        nullable=False,
    )
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    role = Column(String, nullable=False, default="participant")
    joined_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    left_at = Column(DateTime(timezone=True))

    # Local stats per participant (for weighted aggregation).
    local_dataset_size = Column(BigInteger)
    local_data_hash = Column(String)
    last_contribution_round = Column(Integer)

    __table_args__ = (
        UniqueConstraint(
            "federation_id", "project_id", name="federation_participants_fp_uq"
        ),
    )
