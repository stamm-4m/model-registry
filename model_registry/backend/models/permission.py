from sqlalchemy import Column, Text
from sqlalchemy.dialects.postgresql import UUID
import uuid

from model_registry.api.core.database import Base

class Permission(Base):
    __tablename__ = "permissions"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    name = Column(
        Text,
        nullable=False,
        unique=True
    )

    description = Column(
        Text,
        nullable=True
    )