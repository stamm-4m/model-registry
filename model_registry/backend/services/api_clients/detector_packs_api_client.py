"""API client for drift-detector packs + the detector catalog.

``DetectorPacksApiClient`` subclasses BaseApiClient for the auto-CRUD on
``/api/v1/detector_packs/`` and adds two custom calls the scaffold can't
express: ``register`` (multipart upload) and ``activate`` (pin/deploy).
"""

import logging
from typing import Any

from model_registry.backend.services.api_client import authenticated_request
from model_registry.backend.services.api_clients.base_api_client import BaseApiClient

logger = logging.getLogger(__name__)

_SessionData = dict[str, Any]


class DetectorPacksApiClient(BaseApiClient):
    resource_path = "detector_packs"

    def register(
        self,
        filename: str,
        file_bytes: bytes,
        session_data: _SessionData,
        name: str | None = None,
        notes: str | None = None,
        activate: bool = False,
    ) -> tuple[dict[str, Any] | None, _SessionData | None]:
        """Upload a drift_detectors pack archive to the register endpoint."""
        files = {"file": (filename, file_bytes, "application/zip")}
        data: dict[str, Any] = {"activate": str(bool(activate)).lower()}
        if name:
            data["name"] = name
        if notes:
            data["notes"] = notes
        response, session_data = authenticated_request(
            "POST",
            "/api/v1/detector_packs/register",
            session_data,
            files=files,
            data=data,
        )
        if response is None:
            return None, None
        if response.status_code in (200, 201):
            return response.json(), session_data
        try:
            detail = response.json()
        except Exception:
            detail = {"detail": response.text}
        logger.warning(
            "pack register failed status=%s body=%s", response.status_code, detail
        )
        return {
            "error": detail.get("detail", "Upload failed"),
            "status": response.status_code,
        }, session_data

    def activate(
        self, pack_id: str, session_data: _SessionData
    ) -> tuple[dict[str, Any] | None, _SessionData | None]:
        response, session_data = authenticated_request(
            "POST", f"/api/v1/detector_packs/{pack_id}/activate", session_data
        )
        if response is None:
            return None, None
        if response.status_code == 200:
            return response.json(), session_data
        return None, session_data
