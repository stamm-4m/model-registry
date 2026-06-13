from sqlalchemy import Column, String, Boolean, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


import uuid
from model_registry.api.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    external_provider = Column(Text, nullable=True)
    external_id = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    roles = relationship("UserRole", back_populates="user")
    laboratory_users = relationship("LaboratoryUser", back_populates="user")