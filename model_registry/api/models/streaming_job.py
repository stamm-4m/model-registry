"""
Streaming job tracker — cross-process state for the demo streamer.

One row per run. Streamer writes a heartbeat every tick; the dashboard
polls. Stale rows (last_heartbeat older than 30s) are treated as crashed.
"""

from sqlalchemy import Column, DateTime, Float, Integer, Text
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.sql import func

from model_registry.api.core.database import Base


class StreamingJob(Base):
    __tablename__ = "streaming_jobs"

    run_id = Column(UUID(as_uuid=True), primary_key=True)
    status = Column(Text, nullable=False)
    speed = Column(Float, nullable=False, default=1)
    duration_h = Column(Float, nullable=True)
    signals = Column(ARRAY(Text), nullable=False)
    started_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    last_heartbeat = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    bioprocess_t_h = Column(Float, nullable=False, default=0)
    rows_written_total = Column(Integer, nullable=False, default=0)
    pid = Column(Integer, nullable=True)
    last_error = Column(Text, nullable=True)
