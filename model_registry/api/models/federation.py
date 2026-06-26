"""
Federated-learning collaboration spanning multiple participants.

One row = one named federation (e.g. "biomass_fed_v1"). Models that
belong to this federation point back at it via ``models.federation_id``.
The ``current_global_model_id`` always points at the latest aggregated
global model for fast lookup; older rounds remain reachable via
``model_contributions``.
"""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import ARRAY, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID

from model_registry.api.core.database import Base


class Federation(Base):
    __tablename__ = "federations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    slug = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=False)
    description = Column(Text)

    # Whichever org runs the aggregation server.
    coordinator_org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"))

    aggregation_strategy = Column(String, nullable=False)
    privacy_mechanism = Column(String, nullable=False, default="none")
    privacy_params = Column(JSONB, nullable=False, default=dict)

    rounds_planned = Column(Integer, nullable=False, default=1)
    rounds_completed = Column(Integer, nullable=False, default=0)

    status = Column(String, nullable=False, default="planning")

    # Pointer to the current aggregated-global model row (also in models).
    current_global_model_id = Column(UUID(as_uuid=True), ForeignKey("models.id"))

    notes = Column(Text)
    tags = Column(ARRAY(String), nullable=False, default=list)

    created_at = Column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow
    )
    updated_at = Column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow
    )
    created_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
