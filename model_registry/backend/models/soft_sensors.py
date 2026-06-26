import uuid

from sqlalchemy import Column, Text
from sqlalchemy.dialects.postgresql import UUID

from model_registry.api.core.database import Base


class SoftSensor(Base):
    __tablename__ = "soft_sensors"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    path_metadata = Column(Text, nullable=False)
    path_model = Column(Text, nullable=False)
