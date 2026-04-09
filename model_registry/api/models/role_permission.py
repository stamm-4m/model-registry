from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from model_registry.api.core.database import Base

class RolePermission(Base):
    __tablename__ = 'role_permission'

    id = Column(UUID(as_uuid=True), primary_key=True)
    role_id = Column(UUID(as_uuid=True), ForeignKey('roles.id'), nullable=False)
    permission_id = Column(UUID(as_uuid=True), ForeignKey('permissions.id'), nullable=False)

    # Relationships
    role = relationship('Role', back_populates='permissions')
    permission = relationship('Permission', back_populates='roles')

    