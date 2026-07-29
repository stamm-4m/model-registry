"""Dynamic-models service — thin client over /api/v1/dynamic_model (auto-CRUD).

list/create/update/delete for mechanistic models. Never raises; on error
returns None/[] so the page can fall back to a static preview.
"""
import logging
from typing import Any

from model_registry.backend.services.api_clients.base_api_client import BaseApiClient

logger = logging.getLogger(__name__)
_SessionData = dict[str, Any]


class DynamicModelsApiClient(BaseApiClient):
    resource_path = "dynamic_model"


def list_dynamic_models(session_data: _SessionData):
    try:
        rows, session_data = DynamicModelsApiClient().list(session_data)
        return (rows or []), session_data
    except Exception as exc:
        logger.info("list_dynamic_models failed: %s", exc)
        return [], session_data


def create_dynamic_model(session_data: _SessionData, payload: dict):
    try:
        return DynamicModelsApiClient().create(payload, session_data)
    except Exception as exc:
        logger.info("create_dynamic_model failed: %s", exc)
        return None, session_data


def update_dynamic_model(session_data: _SessionData, model_id: str, payload: dict):
    try:
        return DynamicModelsApiClient().update(model_id, payload, session_data)
    except Exception as exc:
        logger.info("update_dynamic_model failed: %s", exc)
        return None, session_data


def delete_dynamic_model(session_data: _SessionData, model_id: str):
    try:
        return DynamicModelsApiClient().delete(model_id, session_data)
    except Exception as exc:
        logger.info("delete_dynamic_model failed: %s", exc)
        return None, session_data
