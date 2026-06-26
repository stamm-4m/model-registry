"""DTOs for department-related entities (department + relations)."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class DepartmentDTO:
    id: str | None = None
    name: str | None = None
    created_at: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DepartmentDTO":
        if not data:
            return cls()
        known = {"id", "name", "created_at"}
        extras = {k: v for k, v in data.items() if k not in known}
        return cls(
            id=data.get("id"),
            name=data.get("name"),
            created_at=data.get("created_at"),
            extra=extras,
        )

    def to_dict(self) -> dict[str, Any]:
        out = {
            "id": self.id,
            "name": self.name,
            "created_at": self.created_at,
        }
        out.update(self.extra)
        return {k: v for k, v in out.items() if v is not None}


@dataclass
class DepartmentLaboratoryDTO:
    id: str | None = None
    department_id: str | None = None
    laboratory_id: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DepartmentLaboratoryDTO":
        data = data or {}
        return cls(
            id=data.get("id"),
            department_id=data.get("department_id"),
            laboratory_id=data.get("laboratory_id"),
        )
