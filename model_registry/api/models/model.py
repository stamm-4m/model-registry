"""
Model registry entry.

Replaces the path-only ``soft_sensors`` row with a richer schema:
structured columns for the things we filter / sort by, a ``config``
JSONB for algorithm-specific hyperparameters, a ``metrics`` JSONB for
training metrics, and explicit lineage + validation + deployment
fields.

Pattern mirrors ``drift_detectors`` (which also uses a JSONB params
column). Replaces or complements ``soft_sensors`` during transition.
See ``PROPOSAL_models_and_projects_yaml_to_db.md`` at the repo root
for the design rationale.
"""
from datetime import datetime
from uuid import uuid4

from sqlalchemy import (Column, String, Text, Boolean, DateTime, Numeric,
                        BigInteger, Integer, ForeignKey, ARRAY)
from sqlalchemy.dialects.postgresql import UUID, JSONB

from model_registry.api.core.database import Base


class Model(Base):
    """One soft-sensor / ML model entry. Same row whether it is a
    single local model, a federated local update, or a federated
    aggregated global model -- the ``federation_*`` columns disambiguate.
    """
    __tablename__ = "models"

    id           = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    slug         = Column(String, nullable=False, unique=True)
    name         = Column(String, nullable=False)
    description  = Column(Text)
    algorithm    = Column(String, nullable=False)
    status       = Column(String, nullable=False, default="draft")
    version      = Column(String, nullable=False, default="1.0.0")

    # Algo-specific config (hyperparameters, architecture).
    config       = Column(JSONB, nullable=False, default=dict)

    # IO contract (sensor names or UUIDs the model expects / emits).
    inputs       = Column(JSONB, nullable=False, default=list)
    outputs      = Column(JSONB, nullable=False, default=list)
    prediction_horizon_min = Column(Numeric)

    # Last-training metrics snapshot.
    metrics      = Column(JSONB, nullable=False, default=dict)

    # Model artifact (binary stays on disk; we only track location).
    artifact_path        = Column(String)
    artifact_format      = Column(String)
    artifact_size_bytes  = Column(BigInteger)
    artifact_sha256      = Column(String)

    # Training context for reproducibility.
    training_dataset_hash    = Column(String)
    training_started_at      = Column(DateTime(timezone=True))
    training_completed_at    = Column(DateTime(timezone=True))
    trained_by_user_id       = Column(UUID(as_uuid=True),
                                       ForeignKey("users.id"))

    # Single-parent lineage (retrains, fine-tunes).
    parent_model_id          = Column(UUID(as_uuid=True),
                                       ForeignKey("models.id"))
    superseded_by_model_id   = Column(UUID(as_uuid=True),
                                       ForeignKey("models.id"))

    # Federated-learning lineage. NULL for single-author models.
    federation_id            = Column(UUID(as_uuid=True),
                                       ForeignKey("federations.id"))
    federation_round         = Column(Integer)
    federation_role          = Column(String)   # 'local_update' | 'aggregated_global'

    # Validation gate (approval before deploy).
    validation_status        = Column(String, nullable=False,
                                       default="pending")
    validated_by_user_id     = Column(UUID(as_uuid=True),
                                       ForeignKey("users.id"))
    validated_at             = Column(DateTime(timezone=True))
    validation_notes         = Column(Text)

    # Deployment metadata.
    deployed_at              = Column(DateTime(timezone=True))
    deployment_notes         = Column(Text)

    # Drift detection link.
    drift_detector_id        = Column(UUID(as_uuid=True),
                                       ForeignKey("drift_detectors.id"))
    last_drift_check_at      = Column(DateTime(timezone=True))
    drift_state              = Column(String)   # 'ok' | 'warning' | 'drift_detected'

    # Documentation + lifecycle bookkeeping.
    notes        = Column(Text)
    tags         = Column(ARRAY(String), nullable=False, default=list)
    is_active    = Column(Boolean, nullable=False, default=True)

    created_at   = Column(DateTime(timezone=True), nullable=False,
                           default=datetime.utcnow)
    updated_at   = Column(DateTime(timezone=True), nullable=False,
                           default=datetime.utcnow)
    created_by_user_id  = Column(UUID(as_uuid=True),
                                  ForeignKey("users.id"))
