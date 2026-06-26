"""Unified Project service.

Replaces the legacy ``ProjectService`` (direct DB access via repository) and
the ``project_api_service`` helpers with a single, session-aware service
that talks to the REST API through ``ProjectsApiClient`` and exposes
``ProjectDTO`` objects.

Conventions (mirroring ``model_service``):
* Every public method accepts ``session_data`` as its first argument.
* Every public method returns ``(result, session_data)`` so refreshed tokens
  are propagated.
* All HTTP traffic flows through ``authenticated_request`` via the
  ``ProjectsApiClient``.

A module-level ``list_projects`` shim is preserved so existing callbacks
that imported it from ``project_api_service`` keep working with a tiny
import change.
"""

from datetime import UTC
from typing import Any
from uuid import UUID

from model_registry.backend.core.exceptions import ProjectInUseException
from model_registry.backend.services.api_clients import ProjectsApiClient
from model_registry.backend.services.dtos import (
    DepartmentRefDTO,
    LaboratoryProjectDTO,
    LaboratoryRefDTO,
    OrganizationRefDTO,
    ProjectDTO,
    ProjectFullDTO,
)

_SessionData = dict[str, Any]


def _coerce_id(value) -> str | None:
    if value is None:
        return None
    if isinstance(value, UUID):
        return str(value)
    return str(value)


class ProjectService:
    """Project operations backed by the FastAPI ``/projects`` endpoints."""

    def __init__(self, client: ProjectsApiClient | None = None):
        self.client = client or ProjectsApiClient()

    # ------------------------------------------------------------------
    # Listing
    # ------------------------------------------------------------------

    def list_projects(
        self, session_data: _SessionData
    ) -> tuple[list[dict[str, Any]] | None, _SessionData | None]:
        """Return the lab-filtered project list (raw dicts).

        Kept as raw dicts because the existing UI consumes the
        ``project_ID`` / ``name`` / ``description`` keys produced by the
        ``/list_projects/`` endpoint directly.
        """
        return self.client.list_projects_for_user(session_data)

    def get_all_projects(
        self, session_data: _SessionData
    ) -> tuple[list[ProjectDTO], _SessionData | None]:
        """Return every project the API exposes as ``ProjectDTO`` instances."""
        data, session_data = self.client.list_all_projects(session_data)
        if data is None:
            return [], session_data
        return [ProjectDTO.from_dict(d) for d in data], session_data

    # ------------------------------------------------------------------
    # Single project
    # ------------------------------------------------------------------

    def get_project(
        self, session_data: _SessionData, project_id
    ) -> tuple[ProjectDTO | None, _SessionData | None]:
        data, session_data = self.client.get_project(
            _coerce_id(project_id), session_data
        )
        if data is None:
            return None, session_data
        return ProjectDTO.from_dict(data), session_data

    def get_full_project(
        self, session_data: _SessionData, project_id
    ) -> tuple[ProjectFullDTO | None, _SessionData | None]:
        """Return project + laboratory + department + organization.

        Composes the hierarchy by chaining the existing CRUD endpoints:
        ``projects`` -> ``laboratory_project`` -> ``laboratories`` ->
        ``department_laboratory`` -> ``departments`` ->
        ``organizations_departments`` -> ``organizations``.
        """
        pid = _coerce_id(project_id)
        proj_data, session_data = self.client.get_project(pid, session_data)
        if proj_data is None:
            return None, session_data

        # project -> laboratory_project -> laboratory
        relations, session_data = self.client.list_laboratory_projects(session_data)
        relation = None
        if relations:
            relation = next(
                (r for r in relations if str(r.get("project_id")) == pid),
                None,
            )

        lab_data: dict[str, Any] = {}
        dept_data: dict[str, Any] = {}
        org_data: dict[str, Any] = {}

        if relation and relation.get("laboratory_id"):
            lab_id = str(relation["laboratory_id"])
            lab_payload, session_data = self.client.get_laboratory(lab_id, session_data)
            lab_data = lab_payload or {}

            # laboratory -> department_laboratory -> department
            dept_links, session_data = self.client.list_department_laboratory(
                session_data
            )
            dept_link = None
            if dept_links:
                dept_link = next(
                    (d for d in dept_links if str(d.get("laboratory_id")) == lab_id),
                    None,
                )

            if dept_link and dept_link.get("department_id"):
                dept_id = str(dept_link["department_id"])
                dept_payload, session_data = self.client.get_department(
                    dept_id, session_data
                )
                dept_data = dept_payload or {}

                # department -> organizations_departments -> organization
                org_links, session_data = self.client.list_organizations_departments(
                    session_data
                )
                org_link = None
                if org_links:
                    org_link = next(
                        (
                            o
                            for o in org_links
                            if str(o.get("department_id")) == dept_id
                        ),
                        None,
                    )
                if org_link and org_link.get("organization_id"):
                    org_payload, session_data = self.client.get_organization(
                        str(org_link["organization_id"]), session_data
                    )
                    org_data = org_payload or {}

        full = ProjectFullDTO(
            project=ProjectDTO.from_dict(proj_data),
            laboratory=LaboratoryRefDTO.from_dict(lab_data),
            department=DepartmentRefDTO.from_dict(dept_data),
            organization=OrganizationRefDTO.from_dict(org_data),
        )
        return full, session_data

    # ------------------------------------------------------------------
    # Mutations
    # ------------------------------------------------------------------

    def create_project(
        self,
        session_data: _SessionData,
        name: str,
        description: str | None = None,
        project_id: str | None = None,
    ) -> tuple[ProjectDTO | None, _SessionData | None]:
        from datetime import datetime

        payload: dict[str, Any] = {
            "name": name,
            # ``Project.created_at`` is a NOT NULL string column, so we set
            # it client-side until the API gains a server-side default.
            "created_at": datetime.now(UTC).isoformat(),
        }
        if description is not None:
            payload["description"] = description
        if project_id is not None:
            # ``project_id`` is the human-readable external code (e.g. P001),
            # which the SQLAlchemy model stores in the ``project_id`` column.
            payload["project_id"] = project_id

        data, session_data = self.client.create_project(payload, session_data)
        if data is None:
            return None, session_data
        return ProjectDTO.from_dict(data), session_data

    def update_project(
        self,
        session_data: _SessionData,
        project_id,
        name: str | None = None,
        description: str | None = None,
        external_id: str | None = None,
    ) -> tuple[ProjectDTO | None, _SessionData | None]:
        payload: dict[str, Any] = {}
        if name is not None:
            payload["name"] = name
        if description is not None:
            payload["description"] = description
        if external_id is not None:
            payload["project_id"] = external_id

        if not payload:
            return self.get_project(session_data, project_id)

        data, session_data = self.client.update_project(
            _coerce_id(project_id), payload, session_data
        )
        if data is None:
            return None, session_data
        return ProjectDTO.from_dict(data), session_data

    # ---- laboratory assignment ---------------------------------------

    def _find_relation_for_project(
        self, session_data: _SessionData, project_id: str
    ) -> tuple[dict[str, Any] | None, _SessionData | None]:
        relations, session_data = self.client.list_laboratory_projects(session_data)
        if not relations:
            return None, session_data
        rel = next(
            (r for r in relations if str(r.get("project_id")) == project_id),
            None,
        )
        return rel, session_data

    def assign_project_to_lab(
        self,
        session_data: _SessionData,
        project_id,
        lab_id,
    ) -> tuple[LaboratoryProjectDTO | None, _SessionData | None]:
        """Create a brand-new ``laboratory_project`` link."""
        data, session_data = self.client.create_laboratory_project(
            _coerce_id(project_id), _coerce_id(lab_id), session_data
        )
        if data is None:
            return None, session_data
        return LaboratoryProjectDTO.from_dict(data), session_data

    def update_project_lab(
        self,
        session_data: _SessionData,
        project_id,
        lab_id,
    ) -> tuple[LaboratoryProjectDTO | None, _SessionData | None]:
        """Update the project's laboratory.

        Mirrors the legacy semantic: PATCH the existing ``laboratory_project``
        row if it exists, otherwise POST a new one.
        """
        pid = _coerce_id(project_id)
        lid = _coerce_id(lab_id)

        relation, session_data = self._find_relation_for_project(session_data, pid)
        if relation:
            data, session_data = self.client.update_laboratory_project(
                str(relation["id"]), lid, session_data
            )
        else:
            data, session_data = self.client.create_laboratory_project(
                pid, lid, session_data
            )

        if data is None:
            return None, session_data
        return LaboratoryProjectDTO.from_dict(data), session_data

    # ---- delete ------------------------------------------------------

    def delete_project(
        self, session_data: _SessionData, project_id
    ) -> tuple[bool, _SessionData | None]:
        """Delete a project, removing its ``laboratory_project`` link first.

        Raises ``ProjectInUseException`` when the API answers with HTTP 409
        (e.g. integrity violation due to remaining children) so the legacy
        callback contract is preserved.
        """
        pid = _coerce_id(project_id)

        # Detach laboratory_project rows first so the FK doesn't block delete.
        relation, session_data = self._find_relation_for_project(session_data, pid)
        if relation:
            status, session_data = self.client.delete_laboratory_project(
                str(relation["id"]), session_data
            )
            if status is None:
                return False, session_data
            if status == 409:
                raise ProjectInUseException(
                    "Cannot delete project: laboratory link is in use."
                )

        status, session_data = self.client.delete_project(pid, session_data)
        if status is None:
            return False, session_data
        if status == 204:
            return True, session_data
        if status == 409:
            raise ProjectInUseException(
                "Cannot delete project: it is referenced by other records."
            )
        return False, session_data


# ---------------------------------------------------------------------------
# Module-level shims (backwards-compat with project_api_service.list_projects)
# ---------------------------------------------------------------------------


def list_projects(
    session_data: _SessionData,
) -> tuple[list[dict[str, Any]] | None, _SessionData | None]:
    """Convenience wrapper kept so callbacks importing the legacy helper
    keep working with a single import path.

    Equivalent to ``ProjectService().list_projects(session_data)``.
    """
    return ProjectService().list_projects(session_data)
