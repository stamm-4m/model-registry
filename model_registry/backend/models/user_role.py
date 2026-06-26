from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from model_registry.api.core.database import Base


class UserRole(Base):
    __tablename__ = "user_role"

    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True, nullable=False
    )
    role_id = Column(
        UUID(as_uuid=True), ForeignKey("roles.id"), primary_key=True, nullable=False
    )
    permission_id = Column(
        UUID(as_uuid=True),
        ForeignKey("permissions.id"),
        primary_key=True,
        nullable=False,
    )
    real_resource_id = Column(UUID(as_uuid=True), primary_key=True, nullable=True)
