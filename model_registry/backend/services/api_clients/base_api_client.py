"""Base ApiClient providing common CRUD helpers over ``/api/v1/<table>/``.

Every concrete client subclasses ``BaseApiClient`` and just sets
``resource_path``. All requests go through ``authenticated_request`` so the
session token is attached/refreshed automatically. Methods return
``(payload, session_data)`` tuples so callers can persist refreshed tokens
back to the Dash session store -- the same convention used by
``model_service`` and ``ProjectsApiClient``.
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


class BaseApiClient:
    """Generic CRUD client for ``/api/v1/<resource_path>/`` endpoints."""

    #: URL segment after ``/api/v1/`` (no surrounding slashes).
    resource_path: str = ""

    def __init__(self, resource_path: Optional[str] = None):
        if resource_path is not None:
            self.resource_path = resource_path
        if not self.resource_path:
            raise ValueError("resource_path must be set on the client")

    # ---- helpers -----------------------------------------------------

    def _base_url(self) -> str:
        return f"/api/v1/{self.resource_path}/"

    def _item_url(self, item_id: str) -> str:
        return f"/api/v1/{self.resource_path}/{item_id}"

    # ---- CRUD --------------------------------------------------------

    def list(
        self,
        session_data: _SessionData,
        offset: int = 0,
        limit: int = 1000,
    ) -> Tuple[Optional[List[Dict[str, Any]]], Optional[_SessionData]]:
        response, session_data = authenticated_request(
            "GET",
            f"{self._base_url()}?offset={offset}&limit={limit}",
            session_data,
        )
        if response is None:
            return None, None
        if response.status_code == 200:
            return response.json(), session_data
        return None, session_data

    def get(
        self, item_id: str, session_data: _SessionData
    ) -> Tuple[Optional[Dict[str, Any]], Optional[_SessionData]]:
        response, session_data = authenticated_request(
            "GET", self._item_url(item_id), session_data
        )
        if response is None:
            return None, None
        if response.status_code == 200:
            return response.json(), session_data
        return None, session_data

    def create(
        self, payload: Dict[str, Any], session_data: _SessionData
    ) -> Tuple[Optional[Dict[str, Any]], Optional[_SessionData]]:
        response, session_data = authenticated_request(
            "POST", self._base_url(), session_data, json=payload
        )
        if response is None:
            return None, None
        if response.status_code in (200, 201):
            return response.json(), session_data
        logger.warning(
            "%s create failed status=%s body=%s",
            self.resource_path, response.status_code, _safe_json(response),
        )
        return None, session_data

    def update(
        self,
        item_id: str,
        payload: Dict[str, Any],
        session_data: _SessionData,
    ) -> Tuple[Optional[Dict[str, Any]], Optional[_SessionData]]:
        response, session_data = authenticated_request(
            "PATCH", self._item_url(item_id), session_data, json=payload
        )
        if response is None:
            return None, None
        if response.status_code == 200:
            return response.json(), session_data
        logger.warning(
            "%s update failed status=%s body=%s",
            self.resource_path, response.status_code, _safe_json(response),
        )
        return None, session_data

    def delete(
        self, item_id: str, session_data: _SessionData
    ) -> Tuple[Optional[int], Optional[_SessionData]]:
        """Returns the raw HTTP status code (204 on success)."""
        response, session_data = authenticated_request(
            "DELETE", self._item_url(item_id), session_data
        )
        if response is None:
            return None, None
        return response.status_code, session_data
