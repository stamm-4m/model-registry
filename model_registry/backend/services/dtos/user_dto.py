"""DTOs for user-related entities (user + role link)."""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class UserDTO:
    id: Optional[str] = None
    email: Optional[str] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    external_provider: Optional[str] = None
    external_id: Optional[str] = None
    created_at: Optional[str] = None
    extra: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UserDTO":
        if not data:
            return cls()
        known = {
            "id", "email", "full_name", "is_active",
            "external_provider", "external_id", "created_at",
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

    def to_dict(self) -> Dict[str, Any]:
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
    id: Optional[str] = None
    user_id: Optional[str] = None
    role_id: Optional[str] = None
    permission_id: Optional[str] = None
    real_resource_id: Optional[str] = None
    extra: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UserRoleDTO":
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
