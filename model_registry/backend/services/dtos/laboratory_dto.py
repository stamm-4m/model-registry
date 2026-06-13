"""DTOs for laboratory-related entities (laboratory + user link)."""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class LaboratoryDTO:
    id: Optional[str] = None
    name: Optional[str] = None
    location: Optional[str] = None
    extra: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LaboratoryDTO":
        if not data:
            return cls()
        known = {"id", "name", "location"}
        extras = {k: v for k, v in data.items() if k not in known}
        return cls(
            id=data.get("id"),
            name=data.get("name"),
            location=data.get("location"),
            extra=extras,
        )

    def to_dict(self) -> Dict[str, Any]:
        out = {"id": self.id, "name": self.name, "location": self.location}
        out.update(self.extra)
        return {k: v for k, v in out.items() if v is not None}


@dataclass
class LaboratoryUserDTO:
    id: Optional[str] = None
    laboratory_id: Optional[str] = None
    user_id: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LaboratoryUserDTO":
        data = data or {}
        return cls(
            id=data.get("id"),
            laboratory_id=data.get("laboratory_id"),
            user_id=data.get("user_id"),
        )
