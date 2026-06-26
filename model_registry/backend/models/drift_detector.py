"""
Configurable drift detection algorithms (PSI, ADWIN, KDQ-tree, PCA-CD, ...).
"""

from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID

from model_registry.api.core.database import Base


class DriftDetector(Base):
    __tablename__ = "drift_detectors"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    detector_id = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=False)
    kind = Column(String, nullable=False)  # 'univariate' | 'multivariate'
    description = Column(Text, nullable=True)
    params = Column(JSONB, nullable=False, default=dict)
    enabled = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=True)
