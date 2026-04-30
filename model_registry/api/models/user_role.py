from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime 
from model_registry.api.core.database import Base

class UserRole(Base):
    __tablename__ = 'user_role'

    id = Column(UUID(as_uuid=True), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), primary_key=True, nullable=False)
    role_id = Column(UUID(as_uuid=True), ForeignKey('roles.id'), primary_key=True, nullable=False)
    resource_type = Column(String, nullable=False)
    permission_id = Column(UUID(as_uuid=True), primary_key=True)
    real_resource_id = Column(UUID(as_uuid=True), primary_key=True)

    # Relationships
    user = relationship("User", back_populates="roles")
    role = relationship("Role", back_populates="user_roles")

