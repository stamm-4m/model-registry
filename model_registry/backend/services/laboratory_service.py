"""Unified Laboratory service backed by ``/api/v1/laboratories/``.

API-client / DTO based, mirrors ``DepartmentService`` / ``OrganizationService``.
* Every public method accepts ``session_data`` as its first argument.
* Every public method returns ``(result, session_data)``.

Laboratory <-> Department association is managed via the
``department_laboratory`` link table; Laboratory <-> User via
``laboratory_user``.
"""

from typing import Any
from uuid import UUID

from model_registry.backend.core.exceptions import LaboratoryInUseException
from model_registry.backend.services.api_clients import (
    DepartmentLaboratoryApiClient,
    DepartmentsApiClient,
    LaboratoriesApiClient,
    LaboratoryUserApiClient,
)
from model_registry.backend.services.dtos import LaboratoryDTO

_SessionData = dict[str, Any]


def _coerce_id(value) -> str | None:
    if value is None:
        return None
    if isinstance(value, UUID):
        return str(value)
    return str(value)


class LaboratoryService:
    """Laboratory operations backed by ``/api/v1/laboratories/``."""

    def __init__(
        self,
        client: LaboratoriesApiClient | None = None,
        dept_lab_client: DepartmentLaboratoryApiClient | None = None,
        lab_user_client: LaboratoryUserApiClient | None = None,
        dept_client: DepartmentsApiClient | None = None,
    ):
        self.client = client or LaboratoriesApiClient()
        self.dept_lab_client = dept_lab_client or DepartmentLaboratoryApiClient()
        self.lab_user_client = lab_user_client or LaboratoryUserApiClient()
        self.dept_client = dept_client or DepartmentsApiClient()

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------

    def get_laboratory(
        self, session_data: _SessionData, laboratory_id
    ) -> tuple[LaboratoryDTO | None, _SessionData | None]:
        data, session_data = self.client.get(_coerce_id(laboratory_id), session_data)
        if data is None:
            return None, session_data
        return LaboratoryDTO.from_dict(data), session_data

    def get_laboratory_all(
        self, session_data: _SessionData
    ) -> tuple[list[LaboratoryDTO], _SessionData | None]:
        data, session_data = self.client.list(session_data)
        if data is None:
            return [], session_data
        return [LaboratoryDTO.from_dict(d) for d in data], session_data

    def get_laboratory_all_with_dept(
        self, session_data: _SessionData
    ) -> tuple[list[tuple[LaboratoryDTO, str | None]], _SessionData | None]:
        """Return [(LaboratoryDTO, department_name), ...] for table rendering."""
        labs, session_data = self.get_laboratory_all(session_data)
        if not labs:
            return [], session_data

        dept_labs, session_data = self.dept_lab_client.list(session_data)
        dept_labs = dept_labs or []
        lab_to_dept: dict[str, str] = {
            str(link.get("laboratory_id")): str(link.get("department_id"))
            for link in dept_labs
            if link.get("laboratory_id") and link.get("department_id")
        }

        depts, session_data = self.dept_client.list(session_data)
        depts = depts or []
        dept_id_to_name: dict[str, str] = {
            str(d.get("id")): d.get("name") for d in depts if d.get("id")
        }

        result: list[tuple[LaboratoryDTO, str | None]] = []
        for lab in labs:
            dept_id = lab_to_dept.get(str(lab.id))
            dept_name = dept_id_to_name.get(dept_id) if dept_id else None
            result.append((lab, dept_name))
        return result, session_data

    def get_by_department(
        self, session_data: _SessionData, department_id
    ) -> tuple[list[LaboratoryDTO], _SessionData | None]:
        did = _coerce_id(department_id)
        dept_labs, session_data = self.dept_lab_client.list(session_data)
        dept_labs = dept_labs or []
        lab_ids = [
            str(link.get("laboratory_id"))
            for link in dept_labs
            if str(link.get("department_id")) == did and link.get("laboratory_id")
        ]
        labs: list[LaboratoryDTO] = []
        for lab_id in lab_ids:
            lab, session_data = self.get_laboratory(session_data, lab_id)
            if lab:
                labs.append(lab)
        return labs, session_data

    # backward-compat alias used by existing callbacks
    def get_labs_by_department(self, session_data, department_id):
        return self.get_by_department(session_data, department_id)

    def get_laboratory_with_dept(
        self, session_data: _SessionData, laboratory_id
    ) -> tuple[tuple[LaboratoryDTO | None, str | None], _SessionData | None]:
        """Return ((lab_dto, department_id), session_data)."""
        lab, session_data = self.get_laboratory(session_data, laboratory_id)
        dept_id, session_data = self.get_department_id_for_laboratory(
            session_data, laboratory_id
        )
        return (lab, dept_id), session_data

    def get_department_id_for_laboratory(
        self, session_data: _SessionData, laboratory_id
    ) -> tuple[str | None, _SessionData | None]:
        lid = _coerce_id(laboratory_id)
        dept_labs, session_data = self.dept_lab_client.list(session_data)
        dept_labs = dept_labs or []
        for link in dept_labs:
            if str(link.get("laboratory_id")) == lid:
                return (
                    str(link.get("department_id"))
                    if link.get("department_id")
                    else None
                ), session_data
        return None, session_data

    def create_laboratory(
        self,
        session_data: _SessionData,
        name: str,
        location: str | None = None,
        department_id: str | None = None,
    ) -> tuple[LaboratoryDTO | None, _SessionData | None]:
        payload: dict[str, Any] = {"name": name}
        if location is not None:
            payload["location"] = location
        data, session_data = self.client.create(payload, session_data)
        if data is None:
            return None, session_data
        lab_dto = LaboratoryDTO.from_dict(data)
        if department_id and lab_dto.id:
            self.dept_lab_client.create(
                {
                    "department_id": _coerce_id(department_id),
                    "laboratory_id": lab_dto.id,
                },
                session_data,
            )
        return lab_dto, session_data

    def update_laboratory(
        self,
        session_data: _SessionData,
        laboratory_id,
        name: str | None = None,
        location: str | None = None,
        department_id: str | None = None,
    ) -> tuple[LaboratoryDTO | None, _SessionData | None]:
        payload: dict[str, Any] = {}
        if name is not None:
            payload["name"] = name
        if location is not None:
            payload["location"] = location

        if payload:
            data, session_data = self.client.update(
                _coerce_id(laboratory_id), payload, session_data
            )
            if data is None:
                lab_dto = None
            else:
                lab_dto = LaboratoryDTO.from_dict(data)
        else:
            lab_dto, session_data = self.get_laboratory(session_data, laboratory_id)

        if department_id is not None:
            lid = _coerce_id(laboratory_id)
            dept_labs, session_data = self.dept_lab_client.list(session_data)
            dept_labs = dept_labs or []
            for link in dept_labs:
                if str(link.get("laboratory_id")) == lid:
                    self.dept_lab_client.update(
                        link.get("id"),
                        {
                            "department_id": _coerce_id(department_id),
                            "laboratory_id": lid,
                        },
                        session_data,
                    )
                    break
            else:
                # No existing link -- create one
                self.dept_lab_client.create(
                    {
                        "department_id": _coerce_id(department_id),
                        "laboratory_id": lid,
                    },
                    session_data,
                )
        return lab_dto, session_data

    def delete_laboratory(
        self, session_data: _SessionData, laboratory_id
    ) -> tuple[bool, _SessionData | None]:
        lid = _coerce_id(laboratory_id)
        # Count dept links
        dept_labs, session_data = self.dept_lab_client.list(session_data)
        dept_labs = dept_labs or []
        link_count = sum(
            1 for link in dept_labs if str(link.get("laboratory_id")) == lid
        )
        if link_count > 0:
            raise LaboratoryInUseException(departments=link_count)

        status, session_data = self.client.delete(lid, session_data)
        if status is None:
            return False, session_data
        if status == 204:
            return True, session_data
        if status == 409:
            raise LaboratoryInUseException(departments=link_count)
        return False, session_data

    def get_laboratory_by_user_id(
        self, session_data: _SessionData, user_id
    ) -> tuple[LaboratoryDTO | None, _SessionData | None]:
        uid = _coerce_id(user_id)
        lab_users, session_data = self.lab_user_client.list(session_data)
        lab_users = lab_users or []
        for link in lab_users:
            if str(link.get("user_id")) == uid and link.get("laboratory_id"):
                return self.get_laboratory(session_data, link["laboratory_id"])
        return None, session_data
