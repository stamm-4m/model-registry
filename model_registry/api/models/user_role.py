from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from model_registry.api.models.laboratory import Laboratory
from datetime import datetime

from model_registry.api.core.database import Base

class UserRole(Base):
    __tablename__ = 'user_role'

    id = Column(UUID(as_uuid=True), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    role_id = Column(UUID(as_uuid=True), ForeignKey('roles.id'), nullable=False)
    laboratory_id = Column(UUID(as_uuid=True), ForeignKey('laboratories.id'), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="roles")
    role = relationship("Role", back_populates="user_roles")
    laboratory = relationship("Laboratory")

