"""DTOs for department-related entities (department + relations)."""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class DepartmentDTO:
    id: Optional[str] = None
    name: Optional[str] = None
    created_at: Optional[str] = None
    extra: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DepartmentDTO":
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

    def to_dict(self) -> Dict[str, Any]:
        out = {
            "id": self.id,
            "name": self.name,
            "created_at": self.created_at,
        }
        out.update(self.extra)
        return {k: v for k, v in out.items() if v is not None}


@dataclass
class DepartmentLaboratoryDTO:
    id: Optional[str] = None
    department_id: Optional[str] = None
    laboratory_id: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DepartmentLaboratoryDTO":
        data = data or {}
        return cls(
            id=data.get("id"),
            department_id=data.get("department_id"),
            laboratory_id=data.get("laboratory_id"),
        )
