"""
Soft-sensor model registry entry.

The class maps the enriched ``soft_sensors`` table, which stores the
structured metadata, lifecycle state, artifacts, and federated-learning
lineage for each soft sensor.
"""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import (
    ARRAY,
    BigInteger,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID

from model_registry.api.core.database import Base


class SoftSensors(Base):
    """One soft-sensor model entry."""

    __tablename__ = "soft_sensors"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    slug = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    algorithm = Column(String, nullable=False)
    status = Column(String, nullable=False, default="draft")
    version = Column(String, nullable=False, default="1.0.0")

    config = Column(JSONB, nullable=False, default=dict)
    inputs = Column(JSONB, nullable=False, default=list)
    outputs = Column(JSONB, nullable=False, default=list)
    prediction_horizon_min = Column(Numeric)
    metrics = Column(JSONB, nullable=False, default=dict)

    artifact_path = Column(String)
    artifact_format = Column(String)
    artifact_size_bytes = Column(BigInteger)
    artifact_sha256 = Column(String)

    training_dataset_hash = Column(String)
    training_started_at = Column(DateTime(timezone=True))
    training_completed_at = Column(DateTime(timezone=True))
    trained_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    parent_model_id = Column(UUID(as_uuid=True), ForeignKey("soft_sensors.id"))
    superseded_by_model_id = Column(
        UUID(as_uuid=True), ForeignKey("soft_sensors.id")
    )

    federation_id = Column(UUID(as_uuid=True), ForeignKey("federations.id"))
    federation_round = Column(Integer)
    federation_role = Column(String)

    validation_status = Column(String, nullable=False, default="pending")
    validated_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    validated_at = Column(DateTime(timezone=True))
    validation_notes = Column(Text)

    deployed_at = Column(DateTime(timezone=True))
    deployment_notes = Column(Text)

    drift_detector_id = Column(
        UUID(as_uuid=True), ForeignKey("drift_detectors.id")
    )
    last_drift_check_at = Column(DateTime(timezone=True))
    drift_state = Column(String)

    notes = Column(Text)
    tags = Column(ARRAY(String), nullable=False, default=list)
    is_active = Column(Boolean, nullable=False, default=True)

    created_at = Column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow
    )
    updated_at = Column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow
    )
    created_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    doi = Column(Text)
    authors = Column(Text)
    learner = Column(Text)
    model_type = Column(Text)
    external_uuid = Column(Text)
    creation_date = Column(Text)
    status_description = Column(Text)

    language = Column(JSONB, nullable=False, default=list)
    packages = Column(JSONB, nullable=False, default=list)
    config_files = Column(JSONB, nullable=False, default=dict)
    input_time_interval = Column(JSONB)
    model_architecture = Column(JSONB)
    training_information = Column(JSONB, nullable=False, default=dict)