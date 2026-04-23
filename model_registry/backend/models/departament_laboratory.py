import uuid
from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from model_registry.api.core.database import Base


class DepartmentLaboratory(Base):
    __tablename__ = "department_laboratory"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    department_id = Column(UUID(as_uuid=True), ForeignKey("departments.id"), primary_key=True)
    laboratory_id = Column(UUID(as_uuid=True), ForeignKey("laboratories.id"), primary_key=True)
    