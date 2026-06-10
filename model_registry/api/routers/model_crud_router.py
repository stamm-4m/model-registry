"""Model-specific CRUD endpoints with template validation.

This module provides validated endpoints for the Model table,
integrating JSON Schema validation based on algorithm templates.
"""

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from model_registry.api.core.database import get_db
from model_registry.api.core.dependencies import require_permission_resource
from model_registry.api.scaffold.crud import _row_to_dict, _coerce_pk
from model_registry.api.models import Model
from model_registry.backend.services.template_validator import (
    validate_model_payload,
    TemplateValidationError,
)


logger = logging.getLogger(__name__)


def register_model_crud(
    router: APIRouter,
    read_perms: Optional[List[str]] = None,
    write_perms: Optional[List[str]] = None,
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
        body: Dict[str, Any],
        db: Session = Depends(get_db),
        user=Depends(require_permission_resource(write_perms, Model.__tablename__)),
    ):
        """Create a model with template validation.

        Validates against JSON Schema if algorithm is specified.
        """
        # Validate template first
        try:
            validate_model_payload(body)
        except TemplateValidationError as e:
            logger.warning(f"Template validation failed: {e}")
            raise HTTPException(
                status_code=422,
                detail=f"Model template validation failed: {'; '.join(e.errors)}"
            )
        except ValueError as e:
            logger.warning(f"Invalid model payload: {e}")
            raise HTTPException(status_code=400, detail=str(e))

        # Create model if validation passes
        try:
            row = Model(**body)
            db.add(row)
            db.commit()
            db.refresh(row)
            return _row_to_dict(row)
        except TypeError as exc:
            db.rollback()
            raise HTTPException(422, f"bad field for models: {exc}")
        except Exception as exc:
            db.rollback()
            logger.error(f"Failed to create model: {exc}")
            raise HTTPException(500, f"Failed to create model: {exc}")

    @router.patch(f"{base}/{{model_id}}", tags=[tag])
    def update_model(
        model_id: str,
        body: Dict[str, Any],
        db: Session = Depends(get_db),
        user=Depends(require_permission_resource(write_perms, Model.__tablename__)),
    ):
        """Update a model with optional template validation.

        If 'algorithm' or 'config' fields are being updated, validates
        the merged payload against the template schema.
        """
        pk = _coerce_pk(Model, model_id)
        row = db.query(Model).filter(pk_col == pk).first()
        if row is None:
            raise HTTPException(404, f"models {model_id} not found")

        # Check if algorithm or config is being updated
        if any(k in body for k in ["algorithm", "config"]):
            # Merge existing row data with update payload for validation
            current_data = _row_to_dict(row)
            merged_payload = {**current_data, **body}

            # Validate merged payload
            try:
                validate_model_payload(merged_payload)
            except TemplateValidationError as e:
                logger.warning(f"Template validation failed on update: {e}")
                raise HTTPException(
                    status_code=422,
                    detail=f"Model template validation failed: {'; '.join(e.errors)}"
                )
            except ValueError as e:
                logger.warning(f"Invalid model payload on update: {e}")
                raise HTTPException(status_code=400, detail=str(e))

        # Update model if validation passes
        valid_cols = {c.name for c in Model.__table__.columns}
        for k, v in body.items():
            if k == pk_name:
                continue
            if k not in valid_cols:
                raise HTTPException(422, f"unknown column '{k}' on models")
            setattr(row, k, v)

        try:
            db.commit()
            db.refresh(row)
            return _row_to_dict(row)
        except Exception as exc:
            db.rollback()
            logger.error(f"Failed to update model: {exc}")
            raise HTTPException(500, f"Failed to update model: {exc}")
