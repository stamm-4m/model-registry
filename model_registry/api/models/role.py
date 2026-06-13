from sqlalchemy import Column, String, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from model_registry.api.models.role_permission import RolePermission
from model_registry.api.core.database import Base

class Role(Base):
    __tablename__ = "roles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=True)

    user_roles = relationship("UserRole", back_populates="role")
    permissions = relationship("RolePermission", back_populates="role")