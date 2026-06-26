"""HTTP client for project-related API endpoints.

Only uses endpoints that already exist in the API:
- ``GET  /list_projects/``                 -> lab-filtered project list (ml_registry_router)
- ``GET  /api/v1/projects/``               -> raw CRUD list (crud_router)
- ``GET  /api/v1/projects/{id}``           -> CRUD get
- ``POST /api/v1/projects/``               -> CRUD create
- ``PATCH /api/v1/projects/{id}``          -> CRUD update
- ``DELETE /api/v1/projects/{id}``         -> CRUD delete
- ``GET  /api/v1/laboratory_project/``     -> CRUD list
- ``POST /api/v1/laboratory_project/``     -> CRUD create (assign lab)
- ``PATCH /api/v1/laboratory_project/{id}``-> CRUD update (re-assign lab)
- ``DELETE /api/v1/laboratory_project/{id}``-> CRUD delete
- ``GET  /api/v1/laboratories/{id}``       -> CRUD get (used to enrich the join)

All requests go through ``authenticated_request`` so the auth token is
attached and refreshed automatically (same pattern as ``model_service``).
Every method returns ``(payload, session_data)`` so the caller can persist
refreshed tokens back into the Dash session store.
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


class ProjectsApiClient:
    """Thin wrapper over the FastAPI project / laboratory_project endpoints."""

    # ---- listing -------------------------------------------------------

    def list_projects_for_user(
        self, session_data: _SessionData
    ) -> tuple[list[dict[str, Any]] | None, _SessionData | None]:
        """``GET /list_projects/`` -- lab-filtered project list."""
        response, session_data = authenticated_request(
            "GET", "/list_projects/", session_data
        )
        if response is None:
            return None, None
        if response.status_code == 200:
            return response.json(), session_data
        return None, session_data

    def list_all_projects(
        self,
        session_data: _SessionData,
        offset: int = 0,
        limit: int = 1000,
    ) -> tuple[list[dict[str, Any]] | None, _SessionData | None]:
        """``GET /api/v1/projects/`` -- raw CRUD listing."""
        response, session_data = authenticated_request(
            "GET",
            f"/api/v1/projects/?offset={offset}&limit={limit}",
            session_data,
        )
        if response is None:
            return None, None
        if response.status_code == 200:
            return response.json(), session_data
        return None, session_data

    # ---- single project ------------------------------------------------

    def get_project(
        self, project_id: str, session_data: _SessionData
    ) -> tuple[dict[str, Any] | None, _SessionData | None]:
        response, session_data = authenticated_request(
            "GET", f"/api/v1/projects/{project_id}", session_data
        )
        if response is None:
            return None, None
        if response.status_code == 200:
            return response.json(), session_data
        return None, session_data

    def create_project(
        self, payload: dict[str, Any], session_data: _SessionData
    ) -> tuple[dict[str, Any] | None, _SessionData | None]:
        response, session_data = authenticated_request(
            "POST", "/api/v1/projects/", session_data, json=payload
        )
        if response is None:
            return None, None
        if response.status_code in (200, 201):
            return response.json(), session_data
        logger.warning(
            "create_project failed status=%s body=%s",
            response.status_code,
            _safe_json(response),
        )
        return None, session_data

    def update_project(
        self,
        project_id: str,
        payload: dict[str, Any],
        session_data: _SessionData,
    ) -> tuple[dict[str, Any] | None, _SessionData | None]:
        response, session_data = authenticated_request(
            "PATCH",
            f"/api/v1/projects/{project_id}",
            session_data,
            json=payload,
        )
        if response is None:
            return None, None
        if response.status_code == 200:
            return response.json(), session_data
        logger.warning(
            "update_project failed status=%s body=%s",
            response.status_code,
            _safe_json(response),
        )
        return None, session_data

    def delete_project(
        self, project_id: str, session_data: _SessionData
    ) -> tuple[int | None, _SessionData | None]:
        """``DELETE /api/v1/projects/{id}``. Returns the HTTP status code."""
        response, session_data = authenticated_request(
            "DELETE", f"/api/v1/projects/{project_id}", session_data
        )
        if response is None:
            return None, None
        return response.status_code, session_data

    # ---- laboratory_project relation ----------------------------------

    def list_laboratory_projects(
        self,
        session_data: _SessionData,
        offset: int = 0,
        limit: int = 1000,
    ) -> tuple[list[dict[str, Any]] | None, _SessionData | None]:
        response, session_data = authenticated_request(
            "GET",
            f"/api/v1/laboratory_project/?offset={offset}&limit={limit}",
            session_data,
        )
        if response is None:
            return None, None
        if response.status_code == 200:
            return response.json(), session_data
        return None, session_data

    def create_laboratory_project(
        self,
        project_id: str,
        laboratory_id: str,
        session_data: _SessionData,
    ) -> tuple[dict[str, Any] | None, _SessionData | None]:
        payload = {
            "project_id": str(project_id),
            "laboratory_id": str(laboratory_id),
        }
        response, session_data = authenticated_request(
            "POST",
            "/api/v1/laboratory_project/",
            session_data,
            json=payload,
        )
        if response is None:
            return None, None
        if response.status_code in (200, 201):
            return response.json(), session_data
        logger.warning(
            "create_laboratory_project failed status=%s body=%s",
            response.status_code,
            _safe_json(response),
        )
        return None, session_data

    def update_laboratory_project(
        self,
        relation_id: str,
        laboratory_id: str,
        session_data: _SessionData,
    ) -> tuple[dict[str, Any] | None, _SessionData | None]:
        response, session_data = authenticated_request(
            "PATCH",
            f"/api/v1/laboratory_project/{relation_id}",
            session_data,
            json={"laboratory_id": str(laboratory_id)},
        )
        if response is None:
            return None, None
        if response.status_code == 200:
            return response.json(), session_data
        logger.warning(
            "update_laboratory_project failed status=%s body=%s",
            response.status_code,
            _safe_json(response),
        )
        return None, session_data

    def delete_laboratory_project(
        self, relation_id: str, session_data: _SessionData
    ) -> tuple[int | None, _SessionData | None]:
        response, session_data = authenticated_request(
            "DELETE",
            f"/api/v1/laboratory_project/{relation_id}",
            session_data,
        )
        if response is None:
            return None, None
        return response.status_code, session_data

    # ---- laboratories (used to enrich the project hierarchy) ---------

    def get_laboratory(
        self, laboratory_id: str, session_data: _SessionData
    ) -> tuple[dict[str, Any] | None, _SessionData | None]:
        response, session_data = authenticated_request(
            "GET", f"/api/v1/laboratories/{laboratory_id}", session_data
        )
        if response is None:
            return None, None
        if response.status_code == 200:
            return response.json(), session_data
        return None, session_data

    # ---- departments / organizations (composite hierarchy) ----------

    def list_department_laboratory(
        self,
        session_data: _SessionData,
        offset: int = 0,
        limit: int = 1000,
    ) -> tuple[list[dict[str, Any]] | None, _SessionData | None]:
        response, session_data = authenticated_request(
            "GET",
            f"/api/v1/department_laboratory/?offset={offset}&limit={limit}",
            session_data,
        )
        if response is None:
            return None, None
        if response.status_code == 200:
            return response.json(), session_data
        return None, session_data

    def list_organizations_departments(
        self,
        session_data: _SessionData,
        offset: int = 0,
        limit: int = 1000,
    ) -> tuple[list[dict[str, Any]] | None, _SessionData | None]:
        response, session_data = authenticated_request(
            "GET",
            f"/api/v1/organizations_departments/?offset={offset}&limit={limit}",
            session_data,
        )
        if response is None:
            return None, None
        if response.status_code == 200:
            return response.json(), session_data
        return None, session_data

    def get_department(
        self, department_id: str, session_data: _SessionData
    ) -> tuple[dict[str, Any] | None, _SessionData | None]:
        response, session_data = authenticated_request(
            "GET", f"/api/v1/departments/{department_id}", session_data
        )
        if response is None:
            return None, None
        if response.status_code == 200:
            return response.json(), session_data
        return None, session_data

    def get_organization(
        self, organization_id: str, session_data: _SessionData
    ) -> tuple[dict[str, Any] | None, _SessionData | None]:
        response, session_data = authenticated_request(
            "GET", f"/api/v1/organizations/{organization_id}", session_data
        )
        if response is None:
            return None, None
        if response.status_code == 200:
            return response.json(), session_data
        return None, session_data
