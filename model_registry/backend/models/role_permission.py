from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
import uuid

from model_registry.api.core.database import Base

class RolePermission(Base):
    __tablename__ = "role_permission"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    role_id = Column(
        UUID(as_uuid=True),
        ForeignKey("roles.id"),
        nullable=False
    )

    permission_id = Column(
        UUID(as_uuid=True),
        ForeignKey("permissions.id"),
        nullable=False
    )