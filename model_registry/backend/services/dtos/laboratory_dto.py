"""DTOs for laboratory-related entities (laboratory + user link)."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class LaboratoryDTO:
    id: str | None = None
    name: str | None = None
    location: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "LaboratoryDTO":
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

    def to_dict(self) -> dict[str, Any]:
        out = {"id": self.id, "name": self.name, "location": self.location}
        out.update(self.extra)
        return {k: v for k, v in out.items() if v is not None}


@dataclass
class LaboratoryUserDTO:
    id: str | None = None
    laboratory_id: str | None = None
    user_id: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "LaboratoryUserDTO":
        data = data or {}
        return cls(
            id=data.get("id"),
            laboratory_id=data.get("laboratory_id"),
            user_id=data.get("user_id"),
        )
