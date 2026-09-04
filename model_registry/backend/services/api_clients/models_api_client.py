"""HTTP client for model-related API endpoints.

Covers both:
- registry endpoints under ``/<project_id>/...`` (list/metadata/update)
- CRUD endpoints under ``/api/v1/models`` and ``/api/v1/project_soft_sensors`` (list/get/create/update/delete)

All requests use ``authenticated_request`` to preserve token refresh behavior.
"""

import logging
from typing import Any

from model_registry.backend.services.api_client import authenticated_request

logger = logging.getLogger(__name__)

_SessionData = dict[str, Any]


def _safe_json(response) -> Any:
    if response is None:
        return None
    try:
        return response.json()
    except Exception:  # pragma: no cover - defensive
        return None


class ModelsApiClient:
    """Thin wrapper over model registry and model CRUD endpoints."""

    # ---- registry endpoints ------------------------------------------

    def list_soft_sensors_for_project(
        self, project_id: str, session_data: _SessionData
    ) -> tuple[list[dict[str, Any]] | None, _SessionData | None]:
        response, session_data = authenticated_request(
            "GET", f"/{project_id}/list_soft_sensors/", session_data
        )
        if response is None:
            return None, None
        if response.status_code == 200:
            return response.json(), session_data
        return None, session_data

    def get_soft_sensor_metadata(
        self,
        project_id: str,
        model_id: str,
        session_data: _SessionData,
    ) -> tuple[dict[str, Any] | None, _SessionData | None]:
        response, session_data = authenticated_request(
            "GET", f"/{project_id}/metadata/{model_id}", session_data
        )
        if response is None:
            return None, None
        if response.status_code == 200:
            return response.json(), session_data
        return None, session_data

    def reload_project(
        self, project_id: str, session_data: _SessionData
    ) -> tuple[dict[str, Any] | None, _SessionData | None]:
        """``POST /<project_id>/reload/`` -- force in-memory registry refresh."""
        response, session_data = authenticated_request(
            "POST", f"/{project_id}/reload/", session_data
        )
        if response is None:
            return None, None
        if response.status_code == 200:
            return response.json(), session_data
        logger.warning(
            "reload_project failed status=%s body=%s",
            response.status_code,
            _safe_json(response),
        )
        return None, session_data

    def explain(
        self,
        project_id: str,
        model_id: str,
        session_data: _SessionData,
        family: str | None = None,
        rows: list[dict[str, Any]] | None = None,
        target_column: str | None = None,
    ) -> tuple[dict[str, Any] | None, _SessionData | None]:
        """``POST /<project_id>/explain/<model_id>`` -- protected XAI endpoint.

        With no ``rows`` the API explains over a sampled background; pass
        ``rows`` (records of an uploaded CSV) + optional ``target_column`` to
        evaluate on real data. Returns the explanation dict (or an ``ok=False``
        dict) and the (possibly refreshed) session.
        """
        body = {"family": family, "rows": rows, "target_column": target_column}
        response, session_data = authenticated_request(
            "POST", f"/{project_id}/explain/{model_id}", session_data, json=body
        )
        if response is None:
            return None, None
        if response.status_code == 200:
            return response.json(), session_data
        logger.warning(
            "explain failed status=%s body=%s",
            response.status_code,
            _safe_json(response),
        )
        return {"ok": False, "reason": f"HTTP {response.status_code}"}, session_data

    def list_soft_sensors_full(
        self, project_id: str, session_data: _SessionData
    ) -> tuple[list[dict[str, Any]] | None, _SessionData | None]:
        response, session_data = authenticated_request(
            "GET", f"/{project_id}/soft_sensors_full/", session_data
        )
        if response is None:
            return None, None
        if response.status_code == 200:
            return response.json(), session_data
        return None, session_data

    def update_registry_soft_sensor(
        self,
        project_id: str,
        model_id: str,
        payload: dict[str, Any],
        session_data: _SessionData,
    ) -> tuple[dict[str, Any] | None, _SessionData | None]:
        response, session_data = authenticated_request(
            "PUT",
            f"/{project_id}/update/{model_id}",
            session_data,
            json=payload,
        )
        if response is None:
            return None, None
        if response.status_code == 200:
            return response.json(), session_data
        logger.warning(
            "update_registry_soft_sensor failed status=%s body=%s",
            response.status_code,
            _safe_json(response),
        )
        return None, session_data

    # ---- soft_sensors CRUD -------------------------------------------------

    def list_soft_sensors_table(
        self,
        session_data: _SessionData,
        offset: int = 0,
        limit: int = 1000,
    ) -> tuple[list[dict[str, Any]] | None, _SessionData | None]:
        response, session_data = authenticated_request(
            "GET",
            f"/api/v1/soft_sensors/?offset={offset}&limit={limit}",
            session_data,
        )
        if response is None:
            return None, None
        if response.status_code == 200:
            return response.json(), session_data
        return None, session_data

    def get_soft_sensor_row(
        self, soft_sensor_id: str, session_data: _SessionData
    ) -> tuple[dict[str, Any] | None, _SessionData | None]:
        response, session_data = authenticated_request(
            "GET", f"/api/v1/soft_sensors/{soft_sensor_id}", session_data
        )
        if response is None:
            return None, None
        if response.status_code == 200:
            return response.json(), session_data
        return None, session_data

    def create_soft_sensor_row(
        self,
        payload: dict[str, Any],
        session_data: _SessionData,
    ) -> tuple[dict[str, Any] | None, _SessionData | None]:
        response, session_data = authenticated_request(
            "POST", "/api/v1/soft_sensors/", session_data, json=payload
        )
        if response is None:
            return None, None
        if response.status_code in (200, 201):
            return response.json(), session_data
        logger.warning(
            "create_soft_sensor_row failed status=%s body=%s",
            response.status_code,
            _safe_json(response),
        )
        return None, session_data

    def update_soft_sensor_row(
        self,
        soft_sensor_id: str,
        payload: dict[str, Any],
        session_data: _SessionData,
    ) -> tuple[dict[str, Any] | None, _SessionData | None]:
        response, session_data = authenticated_request(
            "PATCH",
            f"/api/v1/soft_sensors/{soft_sensor_id}",
            session_data,
            json=payload,
        )
        if response is None:
            return None, None
        if response.status_code == 200:
            return response.json(), session_data
        logger.warning(
            "update_soft_sensor_row failed status=%s body=%s",
            response.status_code,
            _safe_json(response),
        )
        return None, session_data

    def delete_soft_sensor_row(
        self,
        soft_sensor_id: str,
        session_data: _SessionData,
    ) -> tuple[int | None, _SessionData | None]:
        response, session_data = authenticated_request(
            "DELETE", f"/api/v1/soft_sensors/{soft_sensor_id}", session_data
        )
        if response is None:
            return None, None
        return response.status_code, session_data

    # ---- project_soft_sensors CRUD ----------------------------------------

    def list_project_soft_sensors(
        self,
        session_data: _SessionData,
        offset: int = 0,
        limit: int = 1000,
    ) -> tuple[list[dict[str, Any]] | None, _SessionData | None]:
        response, session_data = authenticated_request(
            "GET",
            f"/api/v1/project_soft_sensors/?offset={offset}&limit={limit}",
            session_data,
        )
        if response is None:
            return None, None
        if response.status_code == 200:
            return response.json(), session_data
        return None, session_data

    # ---- experiment_soft_sensors CRUD ------------------------------------

    def list_experiment_soft_sensors(
        self,
        session_data: _SessionData,
        offset: int = 0,
        limit: int = 1000,
    ) -> tuple[list[dict[str, Any]] | None, _SessionData | None]:
        response, session_data = authenticated_request(
            "GET",
            f"/api/v1/experiment_soft_sensors/?offset={offset}&limit={limit}",
            session_data,
        )
        if response is None:
            return None, None
        if response.status_code == 200:
            return response.json(), session_data
        return None, session_data

    def create_experiment_soft_sensor(
        self,
        payload: dict[str, Any],
        session_data: _SessionData,
    ) -> tuple[dict[str, Any] | None, _SessionData | None]:
        response, session_data = authenticated_request(
            "POST", "/api/v1/experiment_soft_sensors/", session_data, json=payload
        )
        if response is None:
            return None, None
        if response.status_code in (200, 201):
            return response.json(), session_data
        logger.warning(
            "create_experiment_soft_sensor failed status=%s body=%s",
            response.status_code,
            _safe_json(response),
        )
        return None, session_data

    def delete_experiment_soft_sensor(
        self,
        relation_id: str,
        session_data: _SessionData,
    ) -> tuple[int | None, _SessionData | None]:
        response, session_data = authenticated_request(
            "DELETE", f"/api/v1/experiment_soft_sensors/{relation_id}", session_data
        )
        if response is None:
            return None, None
        return response.status_code, session_data

    def create_project_soft_sensor(
        self,
        payload: dict[str, Any],
        session_data: _SessionData,
    ) -> tuple[dict[str, Any] | None, _SessionData | None]:
        response, session_data = authenticated_request(
            "POST", "/api/v1/project_soft_sensors/", session_data, json=payload
        )
        if response is None:
            return None, None
        if response.status_code in (200, 201):
            return response.json(), session_data
        logger.warning(
            "create_project_soft_sensor failed status=%s body=%s",
            response.status_code,
            _safe_json(response),
        )
        return None, session_data

    def update_project_soft_sensor(
        self,
        relation_id: str,
        payload: dict[str, Any],
        session_data: _SessionData,
    ) -> tuple[dict[str, Any] | None, _SessionData | None]:
        response, session_data = authenticated_request(
            "PATCH",
            f"/api/v1/project_soft_sensors/{relation_id}",
            session_data,
            json=payload,
        )
        if response is None:
            return None, None
        if response.status_code == 200:
            return response.json(), session_data
        logger.warning(
            "update_project_soft_sensor failed status=%s body=%s",
            response.status_code,
            _safe_json(response),
        )
        return None, session_data

    def delete_project_soft_sensor(
        self,
        relation_id: str,
        session_data: _SessionData,
    ) -> tuple[int | None, _SessionData | None]:
        response, session_data = authenticated_request(
            "DELETE", f"/api/v1/project_soft_sensors/{relation_id}", session_data
        )
        if response is None:
            return None, None
        return response.status_code, session_data
