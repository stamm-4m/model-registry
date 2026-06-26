"""
Generic CRUD scaffold for SQLAlchemy ORM models.

Mounts list / get / create / update / delete endpoints on a router for
any model, applying the registry's existing ``require_permissions(...)``
dependency for auth.

Usage::

    from fastapi import APIRouter
    from model_registry.api.scaffold import register_crud
    from model_registry.api.models import AlertRule

    router = APIRouter(prefix="/api/v1")
    register_crud(router, AlertRule, "alert_rules",
                  read_perms=["VIEW_MODEL"],
                  write_perms=["MANAGE_PROJECT"])

That mounts:
    GET    /api/v1/alert_rules/         -- list
    GET    /api/v1/alert_rules/{id}     -- get one
    POST   /api/v1/alert_rules/         -- create
    PATCH  /api/v1/alert_rules/{id}     -- partial update
    DELETE /api/v1/alert_rules/{id}     -- delete

Body / response shapes are plain ``dict`` (one row = one object). This
keeps the scaffold tiny; a follow-up pass can replace dicts with proper
Pydantic schemas when the consumers want stricter typing.
"""

from .crud import register_crud

__all__ = ["register_crud"]
