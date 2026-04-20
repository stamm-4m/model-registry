# model_registry/api/models/user.py

import uuid
from sqlalchemy import Column, Text, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from model_registry.api.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    full_name = Column(Text, nullable=False)
    email = Column(Text, nullable=False, unique=True)

    password_hash = Column(Text, nullable=True)

    external_provider = Column(Text, nullable=True)
    external_id = Column(Text, nullable=True)

    created_at = Column(DateTime, server_default=func.now())

    is_active = Column(Boolean, server_default="true")