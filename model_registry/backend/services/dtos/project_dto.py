"""Data Transfer Objects for the Projects domain.

These DTOs decouple the Dash UI / service layer from the raw HTTP payload
shape returned by the API. Every field accessed by callbacks is exposed as
an attribute, mirroring the SQLAlchemy ORM objects the legacy
``ProjectService`` used to return so existing callbacks keep working.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ProjectDTO:
    """Single project as exposed by ``/api/v1/projects/`` endpoints."""

    id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    project_id: Optional[str] = None
    created_at: Optional[str] = None
    extra: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProjectDTO":
        if not data:
            return cls()
        known = {"id", "name", "description", "project_id", "created_at"}
        extras = {k: v for k, v in data.items() if k not in known}
        return cls(
            id=data.get("id"),
            name=data.get("name"),
            description=data.get("description"),
            project_id=data.get("project_id"),
            created_at=data.get("created_at"),
            extra=extras,
        )

    def to_dict(self) -> Dict[str, Any]:
        out: Dict[str, Any] = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "project_id": self.project_id,
            "created_at": self.created_at,
        }
        out.update(self.extra)
        return {k: v for k, v in out.items() if v is not None}


@dataclass
class LaboratoryRefDTO:
    id: Optional[str] = None
    name: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LaboratoryRefDTO":
        data = data or {}
        return cls(id=data.get("id"), name=data.get("name"))


@dataclass
class DepartmentRefDTO:
    id: Optional[str] = None
    name: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DepartmentRefDTO":
        data = data or {}
        return cls(id=data.get("id"), name=data.get("name"))


@dataclass
class OrganizationRefDTO:
    id: Optional[str] = None
    name: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OrganizationRefDTO":
        data = data or {}
        return cls(id=data.get("id"), name=data.get("name"))


@dataclass
class ProjectFullDTO:
    """Composite payload returned by ``GET /projects/{id}/full``."""

    project: ProjectDTO
    laboratory: LaboratoryRefDTO
    department: DepartmentRefDTO
    organization: OrganizationRefDTO

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProjectFullDTO":
        data = data or {}
        return cls(
            project=ProjectDTO.from_dict(data.get("project") or {}),
            laboratory=LaboratoryRefDTO.from_dict(data.get("laboratory") or {}),
            department=DepartmentRefDTO.from_dict(data.get("department") or {}),
            organization=OrganizationRefDTO.from_dict(data.get("organization") or {}),
        )

    def as_tuple(self):
        """Return ``(project, laboratory, department, organization)`` for
        backwards-compat with the legacy ``ProjectService.get_full_project``
        unpacking idiom used in callbacks.
        """
        return self.project, self.laboratory, self.department, self.organization


@dataclass
class LaboratoryProjectDTO:
    id: Optional[str] = None
    project_id: Optional[str] = None
    laboratory_id: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LaboratoryProjectDTO":
        data = data or {}
        return cls(
            id=data.get("id"),
            project_id=data.get("project_id"),
            laboratory_id=data.get("laboratory_id"),
        )
