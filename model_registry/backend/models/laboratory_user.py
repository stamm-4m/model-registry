import uuid
from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from model_registry.api.core.database import Base


class LaboratoryUser(Base):
    __tablename__ = "laboratory_user"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    laboratory_id = Column(UUID(as_uuid=True), ForeignKey("laboratories.id"), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)