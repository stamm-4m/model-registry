"""Operator annotations attached to a run."""
from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4
from model_registry.api.core.database import Base


class Annotation(Base):
    __tablename__ = "annotations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"),
                     nullable=False)
    tag = Column(String, nullable=True)
    comment = Column(Text, nullable=True)
    run_id = Column(UUID(as_uuid=True), ForeignKey("runs.id"),
                    nullable=False)
