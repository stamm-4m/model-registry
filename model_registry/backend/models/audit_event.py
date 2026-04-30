"""
Immutable change log for admin CRUD actions.
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4
from model_registry.api.core.database import Base


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    actor_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"),
                           nullable=True)
    action = Column(String, nullable=False)         # 'create' | 'update' | 'delete'
    entity_type = Column(String, nullable=False)    # 'project' | 'experiment' | ...
    entity_id = Column(String, nullable=False)
    detail = Column(Text, nullable=True)
