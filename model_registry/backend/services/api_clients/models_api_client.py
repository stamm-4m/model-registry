"""HTTP client for model-related API endpoints.

Covers both:
- registry endpoints under ``/<project_id>/...`` (list/metadata/update)
- CRUD endpoints under ``/api/v1/models`` and ``/api/v1/project_models``

All requests use ``authenticated_request`` to preserve token refresh behavior.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

from model_registry.backend.services.api_client import authenticated_request

logger = logging.getLogger(__name__)

_SessionData = Dict[str, Any]


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

    def list_models_for_project(
        self, project_id: str, session_data: _SessionData
    ) -> Tuple[Optional[List[Dict[str, Any]]], Optional[_SessionData]]:
        response, session_data = authenticated_request(
            "GET", f"/{project_id}/list_models/", session_data
        )
        if response is None:
            return None, None
        if response.status_code == 200:
            return response.json(), session_data
        return None, session_data

    def get_model_metadata(
        self,
        project_id: str,
        model_id: str,
        session_data: _SessionData,
    ) -> Tuple[Optional[Dict[str, Any]], Optional[_SessionData]]:
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
    ) -> Tuple[Optional[Dict[str, Any]], Optional[_SessionData]]:
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

    def list_models_full(
        self, project_id: str, session_data: _SessionData
    ) -> Tuple[Optional[List[Dict[str, Any]]], Optional[_SessionData]]:
        response, session_data = authenticated_request(
            "GET", f"/{project_id}/models_full/", session_data
        )
        if response is None:
            return None, None
        if response.status_code == 200:
            return response.json(), session_data
        return None, session_data

    def update_registry_model(
        self,
        project_id: str,
        model_id: str,
        payload: Dict[str, Any],
        session_data: _SessionData,
    ) -> Tuple[Optional[Dict[str, Any]], Optional[_SessionData]]:
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
            "update_registry_model failed status=%s body=%s",
            response.status_code,
            _safe_json(response),
        )
        return None, session_data

    # ---- models CRUD -------------------------------------------------

    def list_models_table(
        self,
        session_data: _SessionData,
        offset: int = 0,
        limit: int = 1000,
    ) -> Tuple[Optional[List[Dict[str, Any]]], Optional[_SessionData]]:
        response, session_data = authenticated_request(
            "GET",
            f"/api/v1/models/?offset={offset}&limit={limit}",
            session_data,
        )
        if response is None:
            return None, None
        if response.status_code == 200:
            return response.json(), session_data
        return None, session_data

    def get_model_row(
        self, model_row_id: str, session_data: _SessionData
    ) -> Tuple[Optional[Dict[str, Any]], Optional[_SessionData]]:
        response, session_data = authenticated_request(
            "GET", f"/api/v1/models/{model_row_id}", session_data
        )
        if response is None:
            return None, None
        if response.status_code == 200:
            return response.json(), session_data
        return None, session_data

    def create_model_row(
        self,
        payload: Dict[str, Any],
        session_data: _SessionData,
    ) -> Tuple[Optional[Dict[str, Any]], Optional[_SessionData]]:
        response, session_data = authenticated_request(
            "POST", "/api/v1/models/", session_data, json=payload
        )
        if response is None:
            return None, None
        if response.status_code in (200, 201):
            return response.json(), session_data
        logger.warning(
            "create_model_row failed status=%s body=%s",
            response.status_code,
            _safe_json(response),
        )
        return None, session_data

    def update_model_row(
        self,
        model_row_id: str,
        payload: Dict[str, Any],
        session_data: _SessionData,
    ) -> Tuple[Optional[Dict[str, Any]], Optional[_SessionData]]:
        response, session_data = authenticated_request(
            "PATCH",
            f"/api/v1/models/{model_row_id}",
            session_data,
            json=payload,
        )
        if response is None:
            return None, None
        if response.status_code == 200:
            return response.json(), session_data
        logger.warning(
            "update_model_row failed status=%s body=%s",
            response.status_code,
            _safe_json(response),
        )
        return None, session_data

    def delete_model_row(
        self,
        model_row_id: str,
        session_data: _SessionData,
    ) -> Tuple[Optional[int], Optional[_SessionData]]:
        response, session_data = authenticated_request(
            "DELETE", f"/api/v1/models/{model_row_id}", session_data
        )
        if response is None:
            return None, None
        return response.status_code, session_data

    # ---- project_models CRUD ----------------------------------------

    def list_project_models(
        self,
        session_data: _SessionData,
        offset: int = 0,
        limit: int = 1000,
    ) -> Tuple[Optional[List[Dict[str, Any]]], Optional[_SessionData]]:
        response, session_data = authenticated_request(
            "GET",
            f"/api/v1/project_models/?offset={offset}&limit={limit}",
            session_data,
        )
        if response is None:
            return None, None
        if response.status_code == 200:
            return response.json(), session_data
        return None, session_data

    def create_project_model(
        self,
        payload: Dict[str, Any],
        session_data: _SessionData,
    ) -> Tuple[Optional[Dict[str, Any]], Optional[_SessionData]]:
        response, session_data = authenticated_request(
            "POST", "/api/v1/project_models/", session_data, json=payload
        )
        if response is None:
            return None, None
        if response.status_code in (200, 201):
            return response.json(), session_data
        logger.warning(
            "create_project_model failed status=%s body=%s",
            response.status_code,
            _safe_json(response),
        )
        return None, session_data

    def update_project_model(
        self,
        relation_id: str,
        payload: Dict[str, Any],
        session_data: _SessionData,
    ) -> Tuple[Optional[Dict[str, Any]], Optional[_SessionData]]:
        response, session_data = authenticated_request(
            "PATCH",
            f"/api/v1/project_models/{relation_id}",
            session_data,
            json=payload,
        )
        if response is None:
            return None, None
        if response.status_code == 200:
            return response.json(), session_data
        logger.warning(
            "update_project_model failed status=%s body=%s",
            response.status_code,
            _safe_json(response),
        )
        return None, session_data

    def delete_project_model(
        self,
        relation_id: str,
        session_data: _SessionData,
    ) -> Tuple[Optional[int], Optional[_SessionData]]:
        response, session_data = authenticated_request(
            "DELETE", f"/api/v1/project_models/{relation_id}", session_data
        )
        if response is None:
            return None, None
        return response.status_code, session_data
