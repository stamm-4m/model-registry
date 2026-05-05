"""DTOs for organization-related entities (organization + relations)."""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class OrganizationDTO:
    id: Optional[str] = None
    name: Optional[str] = None
    location: Optional[str] = None
    created_at: Optional[str] = None
    extra: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OrganizationDTO":
        if not data:
            return cls()
        known = {"id", "name", "location", "created_at"}
        extras = {k: v for k, v in data.items() if k not in known}
        return cls(
            id=data.get("id"),
            name=data.get("name"),
            location=data.get("location"),
            created_at=data.get("created_at"),
            extra=extras,
        )

    def to_dict(self) -> Dict[str, Any]:
        out = {
            "id": self.id,
            "name": self.name,
            "location": self.location,
            "created_at": self.created_at,
        }
        out.update(self.extra)
        return {k: v for k, v in out.items() if v is not None}


@dataclass
class OrganizationDepartmentDTO:
    id: Optional[str] = None
    organization_id: Optional[str] = None
    department_id: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OrganizationDepartmentDTO":
        data = data or {}
        return cls(
            id=data.get("id"),
            organization_id=data.get("organization_id"),
            department_id=data.get("department_id"),
        )
