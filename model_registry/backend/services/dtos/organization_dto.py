"""DTOs for organization-related entities (organization + relations)."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class OrganizationDTO:
    id: str | None = None
    name: str | None = None
    location: str | None = None
    created_at: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "OrganizationDTO":
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

    def to_dict(self) -> dict[str, Any]:
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
    id: str | None = None
    organization_id: str | None = None
    department_id: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "OrganizationDepartmentDTO":
        data = data or {}
        return cls(
            id=data.get("id"),
            organization_id=data.get("organization_id"),
            department_id=data.get("department_id"),
        )
