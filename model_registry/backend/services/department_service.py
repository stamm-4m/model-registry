
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from model_registry.backend.core.exceptions import DepartmentInUseException
from model_registry.backend.services.api_clients import (
    DepartmentsApiClient,
    DepartmentLaboratoryApiClient,
    OrganizationsDepartmentsApiClient,
    LaboratoryUserApiClient,
)
from model_registry.backend.services.dtos import DepartmentDTO

_SessionData = Dict[str, Any]

def _coerce_id(value) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, UUID):
        return str(value)
    return str(value)

class DepartmentService:
    """Department operations backed by /api/v1/departments/."""

    def __init__(
        self,
        client: Optional[DepartmentsApiClient] = None,
        dept_lab_client: Optional[DepartmentLaboratoryApiClient] = None,
        org_dept_client: Optional[OrganizationsDepartmentsApiClient] = None,
        lab_user_client: Optional[LaboratoryUserApiClient] = None,
    ):
        self.client = client or DepartmentsApiClient()
        self.dept_lab_client = dept_lab_client or DepartmentLaboratoryApiClient()
        self.org_dept_client = org_dept_client or OrganizationsDepartmentsApiClient()
        self.lab_user_client = lab_user_client or LaboratoryUserApiClient()

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------

    def get_all_departments(
        self, session_data: _SessionData
    ) -> Tuple[List[DepartmentDTO], Optional[_SessionData]]:
        data, session_data = self.client.list(session_data)
        if data is None:
            return [], session_data
        return [DepartmentDTO.from_dict(d) for d in data], session_data

    def get_all_departments_with_org(
        self, session_data: _SessionData
    ) -> Tuple[List[Tuple[DepartmentDTO, Optional[str]]], Optional[_SessionData]]:
        """Return [(DepartmentDTO, organization_name), ...] for table rendering.

        Mirrors the legacy ``DepartmentRepository.get_all`` shape used by
        ``build_table_departments`` so the existing view keeps working.
        """
        depts, session_data = self.get_all_departments(session_data)
        if not depts:
            return [], session_data

        # Build dept_id -> org_id map from link table
        org_depts, session_data = self.org_dept_client.list(session_data)
        org_depts = org_depts or []
        dept_to_org: Dict[str, str] = {
            str(link.get("department_id")): str(link.get("organization_id"))
            for link in org_depts
            if link.get("department_id") and link.get("organization_id")
        }

        # Build org_id -> org_name map
        from model_registry.backend.services.api_clients import OrganizationsApiClient
        orgs, session_data = OrganizationsApiClient().list(session_data)
        orgs = orgs or []
        org_id_to_name: Dict[str, str] = {
            str(o.get("id")): o.get("name") for o in orgs if o.get("id")
        }

        result: List[Tuple[DepartmentDTO, Optional[str]]] = []
        for dept in depts:
            org_id = dept_to_org.get(str(dept.id))
            org_name = org_id_to_name.get(org_id) if org_id else None
            result.append((dept, org_name))
        return result, session_data

    def get_department(
        self, session_data: _SessionData, department_id
    ) -> Tuple[Optional[DepartmentDTO], Optional[_SessionData]]:
        data, session_data = self.client.get(_coerce_id(department_id), session_data)
        if data is None:
            return None, session_data
        return DepartmentDTO.from_dict(data), session_data

    def get_organization_id_for_department(
        self, session_data: _SessionData, department_id
    ) -> Tuple[Optional[str], Optional[_SessionData]]:
        """Return the organization_id linked to a department (via org-dept link)."""
        did = _coerce_id(department_id)
        org_depts, session_data = self.org_dept_client.list(session_data)
        org_depts = org_depts or []
        for link in org_depts:
            if str(link.get("department_id")) == did:
                return str(link.get("organization_id")) if link.get("organization_id") else None, session_data
        return None, session_data

    def get_departments_by_organization(
        self, session_data: _SessionData, organization_id
    ) -> Tuple[List[DepartmentDTO], Optional[_SessionData]]:
        # Find all org-dept links for this org, then fetch each department
        org_depts, session_data = self.org_dept_client.list(session_data)
        org_depts = org_depts or []
        dept_ids = [
            str(d.get("department_id"))
            for d in org_depts
            if str(d.get("organization_id")) == _coerce_id(organization_id) and d.get("department_id")
        ]
        departments = []
        for dept_id in dept_ids:
            dept, session_data = self.get_department(session_data, dept_id)
            if dept:
                departments.append(dept)
        return departments, session_data

    def create_department(
        self, session_data: _SessionData, name: str, organization_id: Optional[str] = None
    ) -> Tuple[Optional[DepartmentDTO], Optional[_SessionData]]:
        payload: Dict[str, Any] = {"name": name}
        # Optionally link to organization via org-dept client
        data, session_data = self.client.create(payload, session_data)
        if data is None:
            return None, session_data
        dept_dto = DepartmentDTO.from_dict(data)
        if organization_id:
            # Create org-dept link
            self.org_dept_client.create(
                {"organization_id": _coerce_id(organization_id), "department_id": dept_dto.id}, session_data
            )
        return dept_dto, session_data

    def update_department(
        self,
        session_data: _SessionData,
        department_id,
        name: Optional[str] = None,
        organization_id: Optional[str] = None,
    ) -> Tuple[Optional[DepartmentDTO], Optional[_SessionData]]:
        payload: Dict[str, Any] = {}
        if name is not None:
            payload["name"] = name
        if not payload and not organization_id:
            return self.get_department(session_data, department_id)
        data, session_data = self.client.update(_coerce_id(department_id), payload, session_data)
        if data is None:
            return None, session_data
        # Optionally update org-dept link
        if organization_id is not None:
            org_depts, session_data = self.org_dept_client.list(session_data)
            org_depts = org_depts or []
            for link in org_depts:
                if str(link.get("department_id")) == _coerce_id(department_id):
                    self.org_dept_client.update(
                        link.get("id"),
                        {"organization_id": _coerce_id(organization_id), "department_id": _coerce_id(department_id)},
                        session_data,
                    )
                    break
        return DepartmentDTO.from_dict(data), session_data

    def delete_department(
        self, session_data: _SessionData, department_id
    ) -> Tuple[bool, Optional[_SessionData]]:
        """Delete a department, raising DepartmentInUseException if labs or users still reference it."""
        did = _coerce_id(department_id)
        deps, session_data = self._dependency_counts(session_data, did)
        if deps["laboratories"] > 0 or deps["users"] > 0:
            raise DepartmentInUseException(users=deps["users"])
        status, session_data = self.client.delete(did, session_data)
        if status is None:
            return False, session_data
        if status == 204:
            return True, session_data
        if status == 409:
            raise DepartmentInUseException(users=deps["users"])
        return False, session_data

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _dependency_counts(
        self, session_data: _SessionData, department_id: str
    ) -> Tuple[Dict[str, int], Optional[_SessionData]]:
        did = str(department_id)
        # Count labs linked to this department
        dept_labs, session_data = self.dept_lab_client.list(session_data)
        dept_labs = dept_labs or []
        lab_ids = [
            str(d.get("laboratory_id"))
            for d in dept_labs
            if str(d.get("department_id")) == did and d.get("laboratory_id")
        ]
        user_count = 0
        if lab_ids:
            lab_users, session_data = self.lab_user_client.list(session_data)
            lab_users = lab_users or []
            user_count = sum(
                1 for lu in lab_users if str(lu.get("laboratory_id")) in lab_ids
            )
        return {
            "laboratories": len(lab_ids),
            "users": user_count,
        }, session_data
