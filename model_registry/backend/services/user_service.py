"""Unified User service backed by ``/api/v1/users/``.

API-client / DTO based, mirrors ``DepartmentService`` / ``OrganizationService``.
* Every public method accepts ``session_data`` as its first argument.
* Every public method returns ``(result, session_data)``.

User <-> Laboratory: ``laboratory_user`` link table.
User <-> Role / model permissions: ``user_role`` link table.
"""

import logging
import uuid as _uuid
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from model_registry.backend.core.exceptions import (
    UserEmailAlreadyExistsException,
    UserHasRolesException,
)
from model_registry.backend.services.api_clients import (
    DepartmentLaboratoryApiClient,
    DepartmentsApiClient,
    LaboratoriesApiClient,
    LaboratoryUserApiClient,
    RolesApiClient,
    UserRolesApiClient,
    UsersApiClient,
)
from model_registry.backend.services.dtos import UserDTO, UserRoleDTO
from model_registry.backend.utils.security import hash_password


logger = logging.getLogger(__name__)

_SessionData = Dict[str, Any]


def _coerce_id(value) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, UUID):
        return str(value)
    return str(value)


class UserService:
    """User operations backed by ``/api/v1/users/``."""

    def __init__(
        self,
        client: Optional[UsersApiClient] = None,
        lab_user_client: Optional[LaboratoryUserApiClient] = None,
        user_role_client: Optional[UserRolesApiClient] = None,
        lab_client: Optional[LaboratoriesApiClient] = None,
        dept_client: Optional[DepartmentsApiClient] = None,
        dept_lab_client: Optional[DepartmentLaboratoryApiClient] = None,
        roles_client: Optional[RolesApiClient] = None,
    ):
        self.client = client or UsersApiClient()
        self.lab_user_client = lab_user_client or LaboratoryUserApiClient()
        self.user_role_client = user_role_client or UserRolesApiClient()
        self.lab_client = lab_client or LaboratoriesApiClient()
        self.dept_client = dept_client or DepartmentsApiClient()
        self.dept_lab_client = dept_lab_client or DepartmentLaboratoryApiClient()
        self.roles_client = roles_client or RolesApiClient()

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------

    def get_user(
        self, session_data: _SessionData, user_id
    ) -> Tuple[Optional[UserDTO], Optional[_SessionData]]:
        data, session_data = self.client.get(_coerce_id(user_id), session_data)
        if data is None:
            return None, session_data
        return UserDTO.from_dict(data), session_data

    def get_all_users(
        self, session_data: _SessionData
    ) -> Tuple[List[UserDTO], Optional[_SessionData]]:
        data, session_data = self.client.list(session_data)
        if data is None:
            return [], session_data
        return [UserDTO.from_dict(d) for d in data], session_data

    def get_all_users_with_department_and_laboratory(
        self, session_data: _SessionData
    ) -> Tuple[
        List[Tuple[UserDTO, Optional[str], Optional[str]]],
        Optional[_SessionData],
    ]:
        """Return ``[(UserDTO, laboratory_name, department_name), ...]``.

        Mirrors the legacy repository method used by ``build_table_users``.
        """
        users, session_data = self.get_all_users(session_data)
        if not users:
            return [], session_data

        lab_users, session_data = self.lab_user_client.list(session_data)
        lab_users = lab_users or []
        user_to_lab: Dict[str, str] = {
            str(link.get("user_id")): str(link.get("laboratory_id"))
            for link in lab_users
            if link.get("user_id") and link.get("laboratory_id")
        }

        labs, session_data = self.lab_client.list(session_data)
        labs = labs or []
        lab_id_to_name: Dict[str, str] = {
            str(lab.get("id")): lab.get("name") for lab in labs if lab.get("id")
        }

        dept_labs, session_data = self.dept_lab_client.list(session_data)
        dept_labs = dept_labs or []
        lab_to_dept: Dict[str, str] = {
            str(link.get("laboratory_id")): str(link.get("department_id"))
            for link in dept_labs
            if link.get("laboratory_id") and link.get("department_id")
        }

        depts, session_data = self.dept_client.list(session_data)
        depts = depts or []
        dept_id_to_name: Dict[str, str] = {
            str(d.get("id")): d.get("name") for d in depts if d.get("id")
        }

        result: List[Tuple[UserDTO, Optional[str], Optional[str]]] = []
        for user in users:
            lab_id = user_to_lab.get(str(user.id))
            lab_name = lab_id_to_name.get(lab_id) if lab_id else None
            dept_id = lab_to_dept.get(lab_id) if lab_id else None
            dept_name = dept_id_to_name.get(dept_id) if dept_id else None
            result.append((user, lab_name, dept_name))
        return result, session_data

    def get_all_users_full(
        self, session_data: _SessionData
    ) -> Tuple[
        List[Tuple[UserDTO, Optional[str], Optional[str], List[str]]],
        Optional[_SessionData],
    ]:
        """Return ``[(UserDTO, lab_name, dept_name, [role_names]), ...]``.

        Fetches user_role + roles in addition to lab/dept so the admin UI
        can display role pills without N+1 calls.
        """
        base, session_data = self.get_all_users_with_department_and_laboratory(
            session_data
        )
        if not base:
            return [], session_data

        user_roles, session_data = self.user_role_client.list(session_data)
        user_roles = user_roles or []
        roles, session_data = self.roles_client.list(session_data)
        roles = roles or []
        role_id_to_name: Dict[str, str] = {
            str(r.get("id")): (r.get("name") or "") for r in roles if r.get("id")
        }

        user_to_role_names: Dict[str, List[str]] = {}
        for link in user_roles:
            # Skip per-resource permission rows; only general role assignments
            # are surfaced as pills (matching the legacy roles modal).
            if link.get("permission_id") is not None:
                continue
            if link.get("real_resource_id") is not None:
                continue
            uid = str(link.get("user_id") or "")
            rid = str(link.get("role_id") or "")
            if not uid or not rid:
                continue
            name = role_id_to_name.get(rid)
            if not name:
                continue
            user_to_role_names.setdefault(uid, []).append(name)

        enriched: List[
            Tuple[UserDTO, Optional[str], Optional[str], List[str]]
        ] = []
        for user, lab_name, dept_name in base:
            names = sorted(set(user_to_role_names.get(str(user.id), [])))
            enriched.append((user, lab_name, dept_name, names))
        return enriched, session_data

    def get_all_roles(
        self, session_data: _SessionData
    ) -> Tuple[List[Dict[str, Any]], Optional[_SessionData]]:
        """Catalogue of roles (used for the Filter-by-role select)."""
        roles, session_data = self.roles_client.list(session_data)
        return roles or [], session_data

    def create_user(
        self,
        session_data: _SessionData,
        name: str,
        email: str,
        password: Optional[str],
        lab_id: str,
    ) -> Tuple[Optional[UserDTO], Optional[_SessionData]]:
        payload: Dict[str, Any] = {
            "full_name": name,
            "email": email,
            "password_hash": hash_password(password) if password else None,
        }
        data, session_data = self.client.create(payload, session_data)
        if data is None:
            # Best-effort detection of duplicate email -- API didn't return body
            raise UserEmailAlreadyExistsException(email)
        user_dto = UserDTO.from_dict(data)
        if lab_id and user_dto.id:
            self.lab_user_client.create(
                {
                    "user_id": user_dto.id,
                    "laboratory_id": _coerce_id(lab_id),
                },
                session_data,
            )
        return user_dto, session_data

    def update_user(
        self,
        session_data: _SessionData,
        user_id,
        name: Optional[str] = None,
        email: Optional[str] = None,
        password: Optional[str] = None,
        lab_id: Optional[str] = None,
    ) -> Tuple[Optional[UserDTO], Optional[_SessionData]]:
        uid = _coerce_id(user_id)
        payload: Dict[str, Any] = {}
        if name is not None:
            payload["full_name"] = name
        if email is not None:
            payload["email"] = email
        if password:
            payload["password_hash"] = hash_password(password)

        if payload:
            data, session_data = self.client.update(uid, payload, session_data)
            user_dto = UserDTO.from_dict(data) if data else None
        else:
            user_dto, session_data = self.get_user(session_data, uid)

        if lab_id is not None:
            lab_users, session_data = self.lab_user_client.list(session_data)
            lab_users = lab_users or []
            existing = next(
                (l for l in lab_users if str(l.get("user_id")) == uid), None
            )
            if existing:
                self.lab_user_client.update(
                    existing.get("id"),
                    {
                        "user_id": uid,
                        "laboratory_id": _coerce_id(lab_id),
                    },
                    session_data,
                )
            else:
                self.lab_user_client.create(
                    {
                        "user_id": uid,
                        "laboratory_id": _coerce_id(lab_id),
                    },
                    session_data,
                )
        return user_dto, session_data

    def delete_user(
        self, session_data: _SessionData, user_id
    ) -> Tuple[bool, Optional[_SessionData]]:
        uid = _coerce_id(user_id)
        roles_count, session_data = self._count_user_roles(session_data, uid)
        if roles_count > 0:
            raise UserHasRolesException(roles_count)
        status, session_data = self.client.delete(uid, session_data)
        if status is None:
            return False, session_data
        if status == 409:
            raise UserHasRolesException(roles_count)
        return status == 204, session_data

    # ------------------------------------------------------------------
    # Lab / department helpers
    # ------------------------------------------------------------------

    def get_lab_id_by_user_id(
        self, session_data: _SessionData, user_id
    ) -> Tuple[Optional[str], Optional[_SessionData]]:
        uid = _coerce_id(user_id)
        lab_users, session_data = self.lab_user_client.list(session_data)
        lab_users = lab_users or []
        for link in lab_users:
            if str(link.get("user_id")) == uid and link.get("laboratory_id"):
                return str(link["laboratory_id"]), session_data
        return None, session_data

    def get_dept_id_by_user_id(
        self, session_data: _SessionData, user_id
    ) -> Tuple[Optional[str], Optional[_SessionData]]:
        lab_id, session_data = self.get_lab_id_by_user_id(session_data, user_id)
        if not lab_id:
            return None, session_data
        dept_labs, session_data = self.dept_lab_client.list(session_data)
        dept_labs = dept_labs or []
        for link in dept_labs:
            if str(link.get("laboratory_id")) == str(lab_id) and link.get(
                "department_id"
            ):
                return str(link["department_id"]), session_data
        return None, session_data

    def get_user_with_laboratory(
        self, session_data: _SessionData, user_id
    ) -> Tuple[Tuple[Optional[UserDTO], Optional[str]], Optional[_SessionData]]:
        user, session_data = self.get_user(session_data, user_id)
        lab_id, session_data = self.get_lab_id_by_user_id(session_data, user_id)
        return (user, lab_id), session_data

    # ------------------------------------------------------------------
    # Role / permission management (user_role link table)
    # ------------------------------------------------------------------

    def _list_user_roles_raw(
        self, session_data: _SessionData, user_id: str
    ) -> Tuple[List[Dict[str, Any]], Optional[_SessionData]]:
        rows, session_data = self.user_role_client.list(session_data)
        rows = rows or []
        return [r for r in rows if str(r.get("user_id")) == str(user_id)], session_data

    def _count_user_roles(
        self, session_data: _SessionData, user_id: str
    ) -> Tuple[int, Optional[_SessionData]]:
        rows, session_data = self._list_user_roles_raw(session_data, user_id)
        return len(rows), session_data

    def get_all_roles_by_user_id(
        self, session_data: _SessionData, user_id
    ) -> Tuple[List[UserRoleDTO], Optional[_SessionData]]:
        uid = _coerce_id(user_id)
        rows, session_data = self._list_user_roles_raw(session_data, uid)
        return [UserRoleDTO.from_dict(r) for r in rows], session_data

    def assign_user_roles(
        self,
        session_data: _SessionData,
        user_id,
        role_ids: List[str],
    ) -> Tuple[None, Optional[_SessionData]]:
        """Replace the user's general (non-permission) role assignments."""
        uid = _coerce_id(user_id)
        rows, session_data = self._list_user_roles_raw(session_data, uid)
        # Delete existing general role rows (no permission_id)
        for row in rows:
            if row.get("permission_id") is None and row.get("id"):
                self.user_role_client.delete(row["id"], session_data)
        for rid in role_ids or []:
            self.user_role_client.create(
                {"user_id": uid, "role_id": _coerce_id(rid)}, session_data
            )
        return None, session_data

    def assign_user_model_roles(
        self,
        session_data: _SessionData,
        user_id,
        role_ids: List[str],
        model_id,
    ) -> Tuple[None, Optional[_SessionData]]:
        uid = _coerce_id(user_id)
        mid = _coerce_id(model_id)
        rows, session_data = self._list_user_roles_raw(session_data, uid)
        # Delete existing rows for this resource
        for row in rows:
            if str(row.get("real_resource_id")) == str(mid) and row.get("id"):
                self.user_role_client.delete(row["id"], session_data)
        for rid in role_ids or []:
            self.user_role_client.create(
                {
                    "user_id": uid,
                    "role_id": _coerce_id(rid),
                    "real_resource_id": mid,
                },
                session_data,
            )
        return None, session_data

    def assign_user_model_permissions(
        self,
        session_data: _SessionData,
        user_id,
        role_ids: List[str],
        permission_ids: List[str],
        model_id,
    ) -> Tuple[None, Optional[_SessionData]]:
        """Assign a (role_id, permission_id) cross product over a model resource.

        Removes prior rows for the user/resource then creates one row per
        (role_id, permission_id) pair, mirroring the legacy repository.
        """
        uid = _coerce_id(user_id)
        mid = _coerce_id(model_id)
        rows, session_data = self._list_user_roles_raw(session_data, uid)
        for row in rows:
            if (
                str(row.get("real_resource_id")) == str(mid)
                and row.get("permission_id") is not None
                and row.get("id")
            ):
                self.user_role_client.delete(row["id"], session_data)
        for rid in role_ids or []:
            for pid in permission_ids or []:
                self.user_role_client.create(
                    {
                        "user_id": uid,
                        "role_id": _coerce_id(rid),
                        "permission_id": _coerce_id(pid),
                        "real_resource_id": mid,
                    },
                    session_data,
                )
        return None, session_data
