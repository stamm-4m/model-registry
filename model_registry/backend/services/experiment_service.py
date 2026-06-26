"""Unified Experiment service backed by ``/api/v1/experiments/``.

API-client / DTO based, mirrors ``ProjectService`` / ``OrganizationService``
conventions:
* Every public method accepts ``session_data`` as its first argument.
* Every public method returns ``(result, session_data)``.
"""

from typing import Any
from uuid import UUID

from model_registry.backend.services.api_clients import ExperimentsApiClient
from model_registry.backend.services.dtos import ExperimentDTO

_SessionData = dict[str, Any]


def _coerce_id(value) -> str | None:
    if value is None:
        return None
    if isinstance(value, UUID):
        return str(value)
    return str(value)


class ExperimentService:
    """Experiment operations backed by ``/api/v1/experiments/``."""

    def __init__(self, client: ExperimentsApiClient | None = None):
        self.client = client or ExperimentsApiClient()

    def get_all_experiments(
        self, session_data: _SessionData
    ) -> tuple[list[ExperimentDTO], _SessionData | None]:
        data, session_data = self.client.list(session_data)
        if data is None:
            return [], session_data
        return [ExperimentDTO.from_dict(d) for d in data], session_data

    def get_experiment_by_id(
        self, session_data: _SessionData, experiment_id
    ) -> tuple[ExperimentDTO | None, _SessionData | None]:
        data, session_data = self.client.get(_coerce_id(experiment_id), session_data)
        if data is None:
            return None, session_data
        return ExperimentDTO.from_dict(data), session_data

    def add_experiment(
        self, session_data: _SessionData, **kwargs
    ) -> tuple[ExperimentDTO | None, _SessionData | None]:
        payload = {k: v for k, v in kwargs.items() if v is not None}
        if "project_id" in payload:
            payload["project_id"] = _coerce_id(payload["project_id"])
        data, session_data = self.client.create(payload, session_data)
        if data is None:
            return None, session_data
        return ExperimentDTO.from_dict(data), session_data

    def update_experiment(
        self,
        session_data: _SessionData,
        experiment_id,
        name: str | None = None,
        project_id: str | None = None,
        description: str | None = None,
        initial_conditions: dict[str, Any] | None = None,
        set_points: dict[str, Any] | None = None,
        start_time: str | None = None,
        end_time: str | None = None,
    ) -> tuple[ExperimentDTO | None, _SessionData | None]:
        payload: dict[str, Any] = {}
        if name is not None:
            payload["name"] = name
        if project_id is not None:
            payload["project_id"] = _coerce_id(project_id)
        if description is not None:
            payload["description"] = description
        if initial_conditions is not None:
            payload["initial_conditions"] = initial_conditions
        if set_points is not None:
            payload["set_points"] = set_points
        if start_time is not None:
            payload["start_time"] = start_time
        if end_time is not None:
            payload["end_time"] = end_time
        if not payload:
            return self.get_experiment_by_id(session_data, experiment_id)
        data, session_data = self.client.update(
            _coerce_id(experiment_id), payload, session_data
        )
        if data is None:
            return None, session_data
        return ExperimentDTO.from_dict(data), session_data

    def delete_experiment(
        self, session_data: _SessionData, experiment_id
    ) -> tuple[bool, _SessionData | None]:
        status, session_data = self.client.delete(
            _coerce_id(experiment_id), session_data
        )
        if status is None:
            return False, session_data
        return status == 204, session_data
