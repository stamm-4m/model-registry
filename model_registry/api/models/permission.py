from sqlalchemy import Column, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from model_registry.api.core.database import Base
from model_registry.api.models.role_permission import RolePermission

class Permission(Base):
    __tablename__ = 'permissions'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text, nullable=True)

    roles = relationship("RolePermission", back_populates="permission")
    