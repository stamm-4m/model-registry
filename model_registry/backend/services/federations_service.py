"""Federated-learning service — thin client over the registry CRUD endpoints.

Reads/writes `federations` and `federation_participants` through
`/api/v1/...` (auto-CRUD scaffold), reusing BaseApiClient so auth/refresh is
handled. Every function returns ``(result, session_data)``. Never raises — on
error returns (None/[], session) so the page can fall back to a static preview.
"""
import logging
from typing import Any

from model_registry.backend.services.api_clients.base_api_client import BaseApiClient

logger = logging.getLogger(__name__)
_SessionData = dict[str, Any]


class FederationsApiClient(BaseApiClient):
    resource_path = "federations"


class FederationParticipantsApiClient(BaseApiClient):
    resource_path = "federation_participants"


class FederationRoundsApiClient(BaseApiClient):
    resource_path = "federation_rounds"


class _ProjectsClient(BaseApiClient):
    resource_path = "projects"


def list_federations(session_data: _SessionData):
    try:
        rows, session_data = FederationsApiClient().list(session_data)
        return (rows or []), session_data
    except Exception as exc:
        logger.info("list_federations failed: %s", exc)
        return [], session_data


def list_participants(session_data: _SessionData):
    try:
        rows, session_data = FederationParticipantsApiClient().list(session_data)
        return (rows or []), session_data
    except Exception as exc:
        logger.info("list_participants failed: %s", exc)
        return [], session_data


def project_label_map(session_data: _SessionData):
    """Return {project_uuid: 'P0001'} so the UI can show project codes not UUIDs."""
    try:
        rows, session_data = _ProjectsClient().list(session_data)
        m = {str(p.get("id")): (p.get("project_id") or p.get("name") or str(p.get("id")))
             for p in (rows or [])}
        return m, session_data
    except Exception as exc:
        logger.info("project_label_map failed: %s", exc)
        return {}, session_data


def list_rounds(session_data: _SessionData):
    try:
        rows, session_data = FederationRoundsApiClient().list(session_data)
        return (rows or []), session_data
    except Exception as exc:
        logger.info("list_rounds failed: %s", exc)
        return [], session_data


def create_federation(session_data: _SessionData, payload: dict):
    try:
        return FederationsApiClient().create(payload, session_data)
    except Exception as exc:
        logger.info("create_federation failed: %s", exc)
        return None, session_data


def update_federation(session_data: _SessionData, fed_id: str, payload: dict):
    try:
        return FederationsApiClient().update(fed_id, payload, session_data)
    except Exception as exc:
        logger.info("update_federation failed: %s", exc)
        return None, session_data


def delete_federation(session_data: _SessionData, fed_id: str):
    try:
        return FederationsApiClient().delete(fed_id, session_data)
    except Exception as exc:
        logger.info("delete_federation failed: %s", exc)
        return None, session_data
