"""
Drift-detection RESULTS (output of running a detector on a run).

Populated by the Airflow DAG (the final task): for each selected
(experiment_drift_detectors) detector+variable, run the pinned detector and
store its result here. FermOps' Health page reads these for the drift grid,
divergence and KPIs. Empty until the DAG runs — FermOps falls back to
synthetic until then.
"""

from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID

from model_registry.api.core.database import Base


class DriftResult(Base):
    __tablename__ = "drift_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    run_id = Column(UUID(as_uuid=True), ForeignKey("runs.id"), nullable=False)
    detector_id = Column(String, nullable=False)
    variable = Column(String, nullable=False)
    phase = Column(String, nullable=True)
    result_type = Column(
        String, nullable=False, default="score"
    )  # score|pointwise|streaming
    score = Column(Float, nullable=True)
    drift = Column(Boolean, nullable=False, default=False)
    details = Column(JSONB, nullable=False, default=dict)
    pack_version = Column(String, nullable=True)  # reproducibility
    computed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=True)
