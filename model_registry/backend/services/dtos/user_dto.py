"""DTOs for user-related entities (user + role link)."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class UserDTO:
    id: str | None = None
    email: str | None = None
    full_name: str | None = None
    is_active: bool | None = None
    external_provider: str | None = None
    external_id: str | None = None
    created_at: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "UserDTO":
        if not data:
            return cls()
        known = {
            "id",
            "email",
            "full_name",
            "is_active",
            "external_provider",
            "external_id",
            "created_at",
        }
        extras = {k: v for k, v in data.items() if k not in known}
        return cls(
            id=data.get("id"),
            email=data.get("email"),
            full_name=data.get("full_name"),
            is_active=data.get("is_active"),
            external_provider=data.get("external_provider"),
            external_id=data.get("external_id"),
            created_at=data.get("created_at"),
            extra=extras,
        )

    def to_dict(self) -> dict[str, Any]:
        out = {
            "id": self.id,
            "email": self.email,
            "full_name": self.full_name,
            "is_active": self.is_active,
            "external_provider": self.external_provider,
            "external_id": self.external_id,
            "created_at": self.created_at,
        }
        out.update(self.extra)
        return {k: v for k, v in out.items() if v is not None}


@dataclass
class UserRoleDTO:
    id: str | None = None
    user_id: str | None = None
    role_id: str | None = None
    permission_id: str | None = None
    real_resource_id: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "UserRoleDTO":
        if not data:
            return cls()
        known = {"id", "user_id", "role_id", "permission_id", "real_resource_id"}
        extras = {k: v for k, v in data.items() if k not in known}
        return cls(
            id=data.get("id"),
            user_id=data.get("user_id"),
            role_id=data.get("role_id"),
            permission_id=data.get("permission_id"),
            real_resource_id=data.get("real_resource_id"),
            extra=extras,
        )
