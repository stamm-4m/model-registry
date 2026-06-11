"""
Per-experiment drift-detector SELECTION.

Which catalog detectors (drift_detectors.detector_id) run for an experiment,
bound to a signal. This is what the Airflow DAG reads to decide what to run
(NOT drift_detectors.enabled, which is only a global default). Mirrors the
per-experiment shape of alert_rules. Written by the FermOps Health page.
"""
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from uuid import uuid4
from model_registry.api.core.database import Base


class ExperimentDriftDetector(Base):
    __tablename__ = "experiment_drift_detectors"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    experiment_id = Column(UUID(as_uuid=True),
                           ForeignKey("experiments.id"), nullable=False)
    detector_id = Column(String, nullable=False)   # -> drift_detectors.detector_id
    # univariate monitor -> 1 variable e.g. {DO}; multivariate -> a set
    # e.g. {DO,pH,Temperature,RPM}. Stored sorted+deduped for stable uniqueness.
    variables = Column(ARRAY(String), nullable=False)
    phase = Column(String, nullable=True)           # optional phase scope
    params_override = Column(JSONB, nullable=False, default=dict)
    enabled = Column(Boolean, nullable=False, default=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, nullable=True)

    __table_args__ = (
        UniqueConstraint("experiment_id", "detector_id", "variables",
                         name="experiment_drift_detectors_uq"),
    )
