import uuid
from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from model_registry.api.core.database import Base


class DepartmentUser(Base):
    __tablename__ = "departments_users"

    id = Column(UUID(as_uuid=True), default=uuid.uuid4)
    department_id = Column(UUID(as_uuid=True), ForeignKey("departments.id"), primary_key=True)
    user_id = Column(UUID(as_uuid=True), primary_key=True)  # ajusta si tienes modelo User