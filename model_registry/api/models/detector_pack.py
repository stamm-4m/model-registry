"""
Drift-detector PACK — a versioned, uploadable source of the detector catalog.

One row per (name, version) of the ``stamm-drift-detectors`` pip package. The
registry UI uploads a slim ``drift_detectors/`` archive; the register endpoint
(routers/detector_packs_router.py) validates it, ingests every detector's
metadata.yaml into the ``drift_detectors`` catalog, and records provenance
here. Exactly one pack per name is ``is_active`` (the pinned/deployed version
the Airflow DAG runs). See [[project_drift_detector_packs]].
"""

from uuid import uuid4

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID

from model_registry.api.core.database import Base


class DetectorPack(Base):
    __tablename__ = "detector_packs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String, nullable=False)  # pip package name
    version = Column(String, nullable=False)  # semver
    source = Column(String, nullable=False, default="upload")  # upload|pip|git
    checksum = Column(String, nullable=True)  # sha256 of the archive
    storage_path = Column(String, nullable=True)  # on-disk slim archive
    detector_count = Column(Integer, nullable=False, default=0)
    detectors = Column(JSONB, nullable=False, default=list)  # list[detector_id]
    is_active = Column(Boolean, nullable=False, default=False)  # pinned/deployed
    notes = Column(Text, nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, nullable=True)

    __table_args__ = (
        UniqueConstraint("name", "version", name="detector_packs_name_version_uq"),
    )
