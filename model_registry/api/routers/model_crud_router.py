"""Model-specific CRUD endpoints with template validation.

This module provides validated endpoints for the Model table,
integrating JSON Schema validation based on algorithm templates.
"""

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from model_registry.api.core.database import get_db
from model_registry.api.core.dependencies import require_permission_resource
from model_registry.api.models import Model
from model_registry.api.scaffold.crud import _coerce_pk, _row_to_dict
from model_registry.backend.services.template_validator import (
    TemplateValidationError,
    validate_model_payload,
)

logger = logging.getLogger(__name__)


def _flatten_model_payload(body: dict[str, Any]) -> dict[str, Any]:
    """Map the JSON-schema–shaped payload from the form to flat DB columns.

    The form (and JSON schema) use nested convenience objects:
      artifact   → artifact_path / artifact_format / artifact_size_bytes / artifact_sha256
      training   → training_dataset_hash + training_information JSONB
      governance → validation_status / validation_notes

    Keys that don't map to a column (ml_task, model_category, …) are left
    in the dict and stripped by the caller against Model.__table__.columns.
    """
    flat = dict(body)

    # artifact block
    artifact = flat.pop("artifact", None)
    if isinstance(artifact, dict):
        flat.setdefault("artifact_path", artifact.get("path"))
        flat.setdefault("artifact_format", artifact.get("format"))
        flat.setdefault("artifact_size_bytes", artifact.get("size_bytes"))
        flat.setdefault("artifact_sha256", artifact.get("sha256"))

    # training block
    training = flat.pop("training", None)
    if isinstance(training, dict):
        flat.setdefault("training_dataset_hash", training.get("dataset_hash", ""))
        # Merge remaining training fields into the training_information JSONB
        ti_extra = {k: v for k, v in training.items() if k != "dataset_hash"}
        if ti_extra:
            existing_ti = flat.get("training_information") or {}
            flat["training_information"] = {**ti_extra, **existing_ti}

    # governance block
    governance = flat.pop("governance", None)
    if isinstance(governance, dict):
        flat.setdefault(
            "validation_status", governance.get("validation_status", "pending")
        )
        flat.setdefault("validation_notes", governance.get("validation_notes"))

    # config must be a dict, never None
    if flat.get("config") is None:
        flat["config"] = {}

    # metrics must be a dict, never None
    if flat.get("metrics") is None:
        flat["metrics"] = {}

    return flat


def register_model_crud(
    router: APIRouter,
    read_perms: list[str] | None = None,
    write_perms: list[str] | None = None,
) -> None:
    """Register validated CRUD endpoints for Model table.

    Adds template validation to create and update operations.

    Args:
        router: FastAPI router
        read_perms: Read permissions required
        write_perms: Write permissions required
    """
    read_perms = read_perms or []
    write_perms = write_perms or []

    pk_col = Model.id
    pk_name = "id"
    base = "/api/v1/models"
    tag = "crud:models"

    @router.post(f"{base}/", tags=[tag], status_code=201)
    def create_model(
        body: dict[str, Any],
        db: Session = Depends(get_db),
        user=Depends(require_permission_resource(write_perms, Model.__tablename__)),
    ):
        """Create a model. Template validation is advisory (warnings only)."""
        # Advisory validation — log warnings but never block the save.
        try:
            validate_model_payload(body)
        except TemplateValidationError as e:
            logger.warning("Template validation warnings (save proceeds): %s", e)
        except ValueError as e:
            logger.debug("Template validation skipped: %s", e)

        # Flatten nested convenience blocks into their actual DB columns.
        flat = _flatten_model_payload(body)

        # Strip keys that are not real columns so Model(**flat) never raises TypeError.
        valid_cols = {c.name for c in Model.__table__.columns}
        flat = {k: v for k, v in flat.items() if k in valid_cols}

        try:
            row = Model(**flat)
            db.add(row)
            db.commit()
            db.refresh(row)
            return _row_to_dict(row)
        except Exception as exc:
            db.rollback()
            logger.error(
                "Failed to create model: %s | payload keys: %s", exc, list(flat.keys())
            )
            raise HTTPException(500, f"Failed to create model: {exc}")

    @router.patch(f"{base}/{{model_id}}", tags=[tag])
    def update_model(
        model_id: str,
        body: dict[str, Any],
        db: Session = Depends(get_db),
        user=Depends(require_permission_resource(write_perms, Model.__tablename__)),
    ):
        """Update a model with optional template validation."""
        pk = _coerce_pk(Model, model_id)
        row = db.query(Model).filter(Model.id == pk).first()
        if row is None:
            raise HTTPException(404, f"models {model_id} not found")

        # Flatten nested blocks before validation/update
        flat = _flatten_model_payload(body)

        # Advisory validation if algorithm/config changing
        if any(k in flat for k in ["algorithm", "config"]):
            try:
                merged = {**_row_to_dict(row), **flat}
                validate_model_payload(merged)
            except TemplateValidationError as e:
                logger.warning(
                    "Template validation warnings on update (proceeding): %s", e
                )
            except ValueError as e:
                logger.debug("Template validation skipped: %s", e)

        valid_cols = {c.name for c in Model.__table__.columns}
        for k, v in flat.items():
            if k == "id" or k not in valid_cols:
                continue
            setattr(row, k, v)

        try:
            db.commit()
            db.refresh(row)
            return _row_to_dict(row)
        except Exception as exc:
            db.rollback()
            logger.error("Failed to update model: %s", exc)
            raise HTTPException(500, f"Failed to update model: {exc}")
