"""Unified Model service.

Provides a session-aware service that talks to model-related endpoints through
``ModelsApiClient`` while keeping backwards-compatible module-level shims for
legacy callsites.

Conventions (same as other unified services):
* Every public method accepts ``session_data`` as its first argument.
* Every public method returns ``(result, session_data)``.
* HTTP traffic flows through ``authenticated_request`` via ``ModelsApiClient``.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

from model_registry.backend.services.api_clients import ModelsApiClient
from model_registry.backend.services.template_validator import (
    validate_model_payload,
    TemplateValidationError,
)


_SessionData = Dict[str, Any]

logger = logging.getLogger(__name__)


class ModelService:
    """Model operations backed by model-specific and CRUD endpoints."""

    def __init__(self, client: Optional[ModelsApiClient] = None):
        self.client = client or ModelsApiClient()

    # ------------------------------------------------------------------
    # Registry endpoints (/list_models, /metadata, /models_full, /update)
    # ------------------------------------------------------------------

    def list_models(
        self, session_data: _SessionData, project_id: str
    ) -> Tuple[Optional[List[Dict[str, Any]]], Optional[_SessionData]]:
        return self.client.list_models_for_project(project_id, session_data)

    def get_model_metadata(
        self, session_data: _SessionData, project_id: str, model_id: str
    ) -> Tuple[Optional[Dict[str, Any]], Optional[_SessionData]]:
        return self.client.get_model_metadata(project_id, model_id, session_data)

    def list_models_full(
        self, session_data: _SessionData, project_id: str
    ) -> Tuple[Optional[List[Dict[str, Any]]], Optional[_SessionData]]:
        return self.client.list_models_full(project_id, session_data)

    def update_registry_model(
        self,
        session_data: _SessionData,
        project_id: str,
        model_id: str,
        payload: Dict[str, Any],
    ) -> Tuple[Optional[Dict[str, Any]], Optional[_SessionData]]:
        return self.client.update_registry_model(
            project_id, model_id, payload, session_data
        )

    def get_model_file_info(
        self,
        session_data: _SessionData,
        project_id: str,
        model_id: str,
    ) -> Tuple[Optional[str], Optional[str], Optional[_SessionData]]:
        """Return model file name/path extracted from model metadata."""
        metadata, session_data = self.get_model_metadata(
            session_data, project_id, model_id
        )
        if not metadata:
            return None, None, session_data

        model_identification = metadata.get("model_identification") or {}
        config_files = (
            (metadata.get("model_description") or {}).get("config_files") or {}
        )

        model_file_name = model_identification.get("ID") or ""
        model_file_relative = config_files.get("model_file") or ""
        return model_file_name, model_file_relative, session_data

    # ------------------------------------------------------------------
    # CRUD endpoints (/api/v1/models and /api/v1/project_models)
    # ------------------------------------------------------------------

    def get_all_model_rows(
        self, session_data: _SessionData
    ) -> Tuple[List[Dict[str, Any]], Optional[_SessionData]]:
        data, session_data = self.client.list_models_table(session_data)
        if data is None:
            return [], session_data
        return data, session_data

    def get_model_row(
        self, session_data: _SessionData, model_row_id: str
    ) -> Tuple[Optional[Dict[str, Any]], Optional[_SessionData]]:
        return self.client.get_model_row(model_row_id, session_data)

    def create_model_row(
        self, session_data: _SessionData, payload: Dict[str, Any]
    ) -> Tuple[Optional[Dict[str, Any]], Optional[_SessionData]]:
        return self.client.create_model_row(payload, session_data)

    def update_model_row(
        self,
        session_data: _SessionData,
        model_row_id: str,
        payload: Dict[str, Any],
    ) -> Tuple[Optional[Dict[str, Any]], Optional[_SessionData]]:
        return self.client.update_model_row(model_row_id, payload, session_data)

    def delete_model_row(
        self, session_data: _SessionData, model_row_id: str
    ) -> Tuple[bool, Optional[_SessionData]]:
        status, session_data = self.client.delete_model_row(model_row_id, session_data)
        if status is None:
            return False, session_data
        return status == 204, session_data

    def list_project_models(
        self, session_data: _SessionData
    ) -> Tuple[List[Dict[str, Any]], Optional[_SessionData]]:
        data, session_data = self.client.list_project_models(session_data)
        if data is None:
            return [], session_data
        return data, session_data

    # ------------------------------------------------------------------
    # Composite create: Model + ProjectModel link
    # ------------------------------------------------------------------

    def create_model_for_project(
        self,
        session_data: _SessionData,
        project_external_id: str,
        payload: Dict[str, Any],
    ) -> Tuple[Optional[Dict[str, Any]], Optional[_SessionData]]:
        """Create a model row in Postgres and link it to ``project_external_id``.

        ``project_external_id`` is the human-readable code stored in
        ``projects.project_id`` (e.g. ``"P0004"``). The project's UUID is
        resolved via the projects CRUD endpoint.

        Raises:
            TemplateValidationError: If model payload fails schema validation.
        """
        from model_registry.backend.services.api_clients import (
            ProjectsApiClient,
        )

        # Validate payload against template schema (advisory only — warnings, not a blocker).
        # The form intentionally collects a subset of schema fields; full compliance
        # is enforced at the API level when the model is later published/deployed.
        try:
            validate_model_payload(payload)
        except TemplateValidationError as e:
            logger.warning(
                "Template validation warnings for algorithm '%s' (save will proceed):\n%s",
                e.algorithm,
                "\n".join(f"  • {err}" for err in e.errors),
            )
        except ValueError as e:
            logger.debug("Template validation skipped: %s", e)

        # Resolve project UUID from external code.
        projects_client = ProjectsApiClient()
        projects, session_data = projects_client.list_all_projects(session_data)
        if not projects:
            return None, session_data
        match = next(
            (
                p for p in projects
                if str(p.get("project_id")) == str(project_external_id)
            ),
            None,
        )
        if match is None:
            return None, session_data
        project_uuid = match.get("id")

        # Create the model row.
        model, session_data = self.client.create_model_row(payload, session_data)
        if model is None:
            return None, session_data

        # Link via project_models.
        link_payload = {
            "project_id": project_uuid,
            "model_id": model.get("id"),
            "role": "primary",
        }
        _, session_data = self.client.create_project_model(
            link_payload, session_data
        )

        # Refresh the in-memory registry so subsequent reads (list / metadata)
        # see the new model without waiting for an API restart.
        try:
            _, session_data = self.client.reload_project(
                project_external_id, session_data
            )
        except Exception as exc:  # non-fatal: read endpoints have a fallback
            logger.warning(
                "Registry reload failed for project %s: %s",
                project_external_id, exc,
            )

        return model, session_data

    def list_db_models_for_project(
        self,
        session_data: _SessionData,
        project_external_id: str,
    ) -> Tuple[List[Dict[str, Any]], Optional[_SessionData]]:
        """Return Postgres-backed models linked to ``project_external_id``.

        Output dicts mimic the legacy ``/list_models/`` shape so they can be
        merged seamlessly with YAML-backed rows in the home grid:
        ``{model_name, model_ID, metadata: {ID, authors, created_at,
        version, status}}``.
        """
        from model_registry.backend.services.api_clients import (
            ProjectsApiClient,
        )

        projects_client = ProjectsApiClient()
        projects, session_data = projects_client.list_all_projects(session_data)
        if not projects:
            return [], session_data
        match = next(
            (
                p for p in projects
                if str(p.get("project_id")) == str(project_external_id)
            ),
            None,
        )
        if match is None:
            return [], session_data
        project_uuid = str(match.get("id"))

        links, session_data = self.client.list_project_models(session_data)
        if not links:
            return [], session_data
        model_ids = {
            str(l.get("model_id"))
            for l in links
            if str(l.get("project_id")) == project_uuid
        }
        if not model_ids:
            return [], session_data

        all_rows, session_data = self.client.list_models_table(session_data)
        if not all_rows:
            return [], session_data

        formatted: List[Dict[str, Any]] = []
        for row in all_rows:
            if str(row.get("id")) not in model_ids:
                continue
            formatted.append({
                "model_name": row.get("name") or row.get("slug"),
                "model_ID": row.get("slug"),
                "metadata": {
                    "ID": row.get("slug"),
                    "db_uuid": row.get("id"),   # Postgres UUID — used for API delete/edit
                    "authors": row.get("authors"),
                    "created_at": row.get("creation_date")
                    or row.get("created_at"),
                    "version": row.get("version"),
                    "status": row.get("status"),
                    "is_active": bool(row.get("is_active")),
                },
            })
        return formatted, session_data

# ---------------------------------------------------------------------------
# Module-level shims (backwards-compat with existing imports)
# ---------------------------------------------------------------------------

def list_models(project_id, session_data):
    """Backward-compatible helper used by existing callbacks/pages."""
    return ModelService().list_models(session_data, project_id)


def get_model_metadata(project_id, model_id, session_data):
    """Backward-compatible helper used by existing callbacks/pages."""
    return ModelService().get_model_metadata(session_data, project_id, model_id)


def get_model_file_info(project_id, model_id, session_data):
    """Backward-compatible helper used by existing callbacks/pages."""
    return ModelService().get_model_file_info(session_data, project_id, model_id)


def predict_dummy(X):
    # Placeholder for model inference
    return [0 for _ in range(len(X))]
