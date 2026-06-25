"""Backend (UI) explainability client — HTTP only.

This module is a THIN wrapper over the protected registry endpoint
``POST /{project_id}/explain/{model_id}`` (see
`model_registry/api/services/explainability.py`). The Dash backend is a client:
it does NOT load artifacts, resolve paths, touch the DB, or import the API
internals — all of that lives behind the endpoint and the single auth boundary.
All traffic goes through `ModelsApiClient` / `authenticated_request` (JWT +
refresh), exactly like every other backend → registry call.

Both helpers return the explanation dict (with `ok` and any of importances /
rules_text / subtree / coef / pdp / shap_summary / shap_instances /
perm_importance / capabilities). On any failure they return `{"ok": False,
...}` so the page falls back to placeholders. They never raise.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from model_registry.backend.services.api_clients.models_api_client import ModelsApiClient

logger = logging.getLogger(__name__)


def explain(project_id, model_id, family=None, session_data=None) -> Dict[str, Any]:
    """Sampled-background explanations for one model (read path)."""
    if not session_data:
        return {"ok": False, "reason": "no auth session"}
    try:
        result, _ = ModelsApiClient().explain(
            project_id, model_id, session_data, family=family)
        return result or {"ok": False, "reason": "no response from registry"}
    except Exception as exc:
        logger.info("xai explain HTTP failed for %s/%s: %s", project_id, model_id, exc)
        return {"ok": False, "reason": str(exc)}


def explain_with_data(project_id, model_id, family, rows, target_column=None,
                      session_data=None) -> Dict[str, Any]:
    """Explanations evaluated on uploaded data (`rows` = CSV records)."""
    if not session_data:
        return {"ok": False, "reason": "no auth session"}
    try:
        result, _ = ModelsApiClient().explain(
            project_id, model_id, session_data,
            family=family, rows=rows, target_column=target_column)
        return result or {"ok": False, "reason": "no response from registry"}
    except Exception as exc:
        logger.info("xai explain_with_data HTTP failed for %s/%s: %s",
                    project_id, model_id, exc)
        return {"ok": False, "reason": str(exc)}
