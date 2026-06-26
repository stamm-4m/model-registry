"""
Soft sensor registry entry. The DB row stores file PATHS to the model
artefacts on disk (path_metadata = YAML config, path_model = pickled
predictor). The actual model isn't pulled into Postgres.

Schema reminder:
    soft_sensors(id uuid PK, path_metadata text, path_model text)
    UNIQUE (path_metadata, path_model)
"""

from uuid import uuid4

from sqlalchemy import Column, Text
from sqlalchemy.dialects.postgresql import UUID

from model_registry.api.core.database import Base


class SoftSensor(Base):
    __tablename__ = "soft_sensors"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    path_metadata = Column(Text, nullable=False)
    path_model = Column(Text, nullable=False)
