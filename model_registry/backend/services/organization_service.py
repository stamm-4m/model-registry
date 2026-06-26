"""Unified Organization service.

Replaces the legacy direct-DB ``OrganizationService`` with a session-aware
service that talks to the REST API through ``OrganizationsApiClient`` and
exposes ``OrganizationDTO`` objects. Method names match the legacy ones so
the only required change at callsites is passing ``session_data`` first.

Conventions (mirroring ``model_service`` / ``ProjectService``):
* Every public method accepts ``session_data`` as its first argument.
* Every public method returns ``(result, session_data)`` so refreshed tokens
  are propagated back to the Dash session store.
"""

from typing import Any
from uuid import UUID

from model_registry.backend.core.exceptions import OrganizationInUseException
from model_registry.backend.services.api_clients import (
    DepartmentLaboratoryApiClient,
    LaboratoryUserApiClient,
    OrganizationsApiClient,
    OrganizationsDepartmentsApiClient,
)
from model_registry.backend.services.dtos import OrganizationDTO

_SessionData = dict[str, Any]


def _coerce_id(value) -> str | None:
    if value is None:
        return None
    if isinstance(value, UUID):
        return str(value)
    return str(value)


class OrganizationService:
    """Organization operations backed by ``/api/v1/organizations/``."""

    def __init__(
        self,
        client: OrganizationsApiClient | None = None,
        org_dept_client: OrganizationsDepartmentsApiClient | None = None,
        dept_lab_client: DepartmentLaboratoryApiClient | None = None,
        lab_user_client: LaboratoryUserApiClient | None = None,
    ):
        self.client = client or OrganizationsApiClient()
        self.org_dept_client = org_dept_client or OrganizationsDepartmentsApiClient()
        self.dept_lab_client = dept_lab_client or DepartmentLaboratoryApiClient()
        self.lab_user_client = lab_user_client or LaboratoryUserApiClient()

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------

    def get_all_organizations(
        self, session_data: _SessionData
    ) -> tuple[list[OrganizationDTO], _SessionData | None]:
        data, session_data = self.client.list(session_data)
        if data is None:
            return [], session_data
        return [OrganizationDTO.from_dict(d) for d in data], session_data

    def get_organization(
        self, session_data: _SessionData, organization_id
    ) -> tuple[OrganizationDTO | None, _SessionData | None]:
        data, session_data = self.client.get(_coerce_id(organization_id), session_data)
        if data is None:
            return None, session_data
        return OrganizationDTO.from_dict(data), session_data

    def create_organization(
        self, session_data: _SessionData, name: str, location: str | None = None
    ) -> tuple[OrganizationDTO | None, _SessionData | None]:
        payload: dict[str, Any] = {"name": name}
        if location is not None:
            payload["location"] = location
        data, session_data = self.client.create(payload, session_data)
        if data is None:
            return None, session_data
        return OrganizationDTO.from_dict(data), session_data

    def update_organization(
        self,
        session_data: _SessionData,
        organization_id,
        name: str | None = None,
        location: str | None = None,
    ) -> tuple[OrganizationDTO | None, _SessionData | None]:
        payload: dict[str, Any] = {}
        if name is not None:
            payload["name"] = name
        if location is not None:
            payload["location"] = location
        if not payload:
            return self.get_organization(session_data, organization_id)
        data, session_data = self.client.update(
            _coerce_id(organization_id), payload, session_data
        )
        if data is None:
            return None, session_data
        return OrganizationDTO.from_dict(data), session_data

    def delete_organization(
        self, session_data: _SessionData, organization_id
    ) -> tuple[bool, _SessionData | None]:
        """Delete an organization, raising ``OrganizationInUseException``
        when departments or downstream users still reference it.

        The dependency check is performed by walking the link tables via
        their API clients (organizations_departments -> department_laboratory
        -> laboratory_user) so the rule stays equivalent to the legacy
        ``get_dependency_counts`` in ``OrganizationRepository``.
        """
        oid = _coerce_id(organization_id)

        deps, session_data = self._dependency_counts(session_data, oid)
        if deps["departments"] > 0 or deps["users"] > 0:
            raise OrganizationInUseException(
                departments=deps["departments"],
                users=deps["users"],
            )

        status, session_data = self.client.delete(oid, session_data)
        if status is None:
            return False, session_data
        if status == 204:
            return True, session_data
        if status == 409:
            # API-level integrity guard caught a residual FK -- surface as
            # in-use so the UI shows a friendly message rather than a 500.
            raise OrganizationInUseException(
                departments=deps["departments"],
                users=deps["users"],
            )
        return False, session_data

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _dependency_counts(
        self, session_data: _SessionData, organization_id: str
    ) -> tuple[dict[str, int], _SessionData | None]:
        """Replicates ``OrganizationRepository.get_dependency_counts`` over HTTP."""
        oid = str(organization_id)

        org_depts, session_data = self.org_dept_client.list(session_data)
        org_depts = org_depts or []
        dept_ids = [
            str(d.get("department_id"))
            for d in org_depts
            if str(d.get("organization_id")) == oid and d.get("department_id")
        ]

        lab_count = 0
        user_count = 0
        lab_ids: list[str] = []

        if dept_ids:
            dept_labs, session_data = self.dept_lab_client.list(session_data)
            dept_labs = dept_labs or []
            lab_ids = [
                str(d.get("laboratory_id"))
                for d in dept_labs
                if str(d.get("department_id")) in dept_ids and d.get("laboratory_id")
            ]
            lab_count = len(lab_ids)

        if lab_ids:
            lab_users, session_data = self.lab_user_client.list(session_data)
            lab_users = lab_users or []
            user_count = sum(
                1 for lu in lab_users if str(lu.get("laboratory_id")) in lab_ids
            )

        return (
            {
                "departments": len(dept_ids),
                "laboratories": lab_count,
                "users": user_count,
            },
            session_data,
        )
