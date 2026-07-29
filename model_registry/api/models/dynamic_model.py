"""Dynamic (mechanistic / kinetic) model registry row.

Thin core columns + a rich `information` JSON blob holding the detailed
metadata (type, process, state variables, parameters, equations, assumptions,
references, run conditions, calibration). `url_endpoint` is the optional
remote-service option (a lab-hosted solver). See [[project_dynamic_models_view]].
"""
from uuid import uuid4

from sqlalchemy import JSON, Column, String
from sqlalchemy.dialects.postgresql import UUID

from model_registry.api.core.database import Base


class DynamicModel(Base):
    __tablename__ = "dynamic_model"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String)
    version = Column(String)
    url_endpoint = Column(String)
    information = Column(JSON)
    model_registry_id = Column(UUID(as_uuid=True))
