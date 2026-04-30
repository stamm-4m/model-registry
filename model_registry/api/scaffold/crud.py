"""
The CRUD-route generator.

Returns a closure that registers 5 endpoints on the given router. Auth is
applied via the registry's existing ``require_permissions(...)`` dependency.

Limitations (intentional, for a v1 scaffold):
  * No relationship-eager-loading. Joins / nested data shapes need
    hand-written endpoints.
  * No filtering beyond ``offset`` / ``limit`` on list. Add ``?field=value``
    filters later.
  * Body schemas are plain ``dict``; Pydantic v2 ``BaseModel`` schemas
    can be added per-table if FermOps wants stricter typing on a route.
  * ``PATCH`` semantics: any field NOT supplied stays unchanged; supplied
    ``None`` writes NULL.
"""

import logging
from typing import Any, Dict, List, Optional, Type
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from model_registry.api.core.database import Base, get_db
from model_registry.api.core.dependencies import require_permission_resource

logger = logging.getLogger(__name__)


def _row_to_dict(row) -> Dict[str, Any]:
    """Serialize a SQLAlchemy row to a plain dict.

    UUID -> str, datetime -> ISO string, all else -> as-is.
    """
    out: Dict[str, Any] = {}
    for col in row.__table__.columns:
        val = getattr(row, col.name)
        if isinstance(val, UUID):
            val = str(val)
        elif hasattr(val, "isoformat"):
            val = val.isoformat()
        out[col.name] = val
    return out


def _coerce_pk(model: Type[Base], pk_value: str):
    """Coerce a string-as-path-param to the model's actual PK column type."""
    pk_col = list(model.__table__.primary_key.columns)[0]
    pk_type_str = str(pk_col.type)
    if "UUID" in pk_type_str.upper():
        try:
            return UUID(pk_value)
        except ValueError:
            raise HTTPException(400, f"invalid UUID: {pk_value}")
    return pk_value


def register_crud(
    router: APIRouter,
    model: Type[Base],
    path_prefix: str,
    *,
    read_perms: Optional[List[str]] = None,
    write_perms: Optional[List[str]] = None,
    tag: Optional[str] = None,
) -> None:
    """Register list/get/create/update/delete endpoints for ``model``."""
    read_perms = read_perms or []
    write_perms = write_perms or []
    if not read_perms:
        raise ValueError("read_perms must be provided")
    if not write_perms:
        raise ValueError("write_perms must be provided")
    tag = tag or path_prefix
    base = f"/{path_prefix}"

    pk_col = list(model.__table__.primary_key.columns)[0]
    pk_name = pk_col.name

    @router.get(f"{base}/", tags=[tag])
    def _list(
        offset: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000),
        db: Session = Depends(get_db),
        user=Depends(require_permission_resource(read_perms, model.__tablename__)),
    ):
        rows = db.query(model).offset(offset).limit(limit).all()
        return [_row_to_dict(r) for r in rows]

    @router.get(f"{base}/{{item_id}}", tags=[tag])
    def _get(
        item_id: str,
        db: Session = Depends(get_db),
        user=Depends(require_permission_resource(read_perms, model.__tablename__)),
    ):
        pk = _coerce_pk(model, item_id)
        row = db.query(model).filter(pk_col == pk).first()
        if row is None:
            raise HTTPException(404, f"{model.__tablename__} {item_id} not found")
        return _row_to_dict(row)

    @router.post(f"{base}/", tags=[tag], status_code=201)
    def _create(
        body: Dict[str, Any],
        db: Session = Depends(get_db),
        user=Depends(require_permission_resource(write_perms, model.__tablename__)),
    ):
        # Drop the PK if the client sent one and the column has a default --
        # we want server-side UUIDs.
        if pk_name in body and pk_col.default is not None:
            body = {k: v for k, v in body.items() if k != pk_name}
        try:
            row = model(**body)
            db.add(row)
            db.commit()
            db.refresh(row)
        except TypeError as exc:
            db.rollback()
            raise HTTPException(422, f"bad field for {model.__tablename__}: {exc}")
        except IntegrityError as exc:
            db.rollback()
            raise HTTPException(409, f"integrity error: {exc.orig}")
        return _row_to_dict(row)

    @router.patch(f"{base}/{{item_id}}", tags=[tag])
    def _update(
        item_id: str,
        body: Dict[str, Any],
        db: Session = Depends(get_db),
        user=Depends(require_permission_resource(write_perms, model.__tablename__)),
    ):
        pk = _coerce_pk(model, item_id)
        row = db.query(model).filter(pk_col == pk).first()
        if row is None:
            raise HTTPException(404, f"{model.__tablename__} {item_id} not found")
        valid_cols = {c.name for c in model.__table__.columns}
        for k, v in body.items():
            if k == pk_name:
                continue   # never allow changing the PK
            if k not in valid_cols:
                raise HTTPException(422, f"unknown column '{k}' on {model.__tablename__}")
            setattr(row, k, v)
        try:
            db.commit()
            db.refresh(row)
        except IntegrityError as exc:
            db.rollback()
            raise HTTPException(409, f"integrity error: {exc.orig}")
        return _row_to_dict(row)

    @router.delete(f"{base}/{{item_id}}", tags=[tag], status_code=204)
    def _delete(
        item_id: str,
        db: Session = Depends(get_db),
        user=Depends(require_permission_resource(write_perms, model.__tablename__)),
    ):
        pk = _coerce_pk(model, item_id)
        row = db.query(model).filter(pk_col == pk).first()
        if row is None:
            raise HTTPException(404, f"{model.__tablename__} {item_id} not found")
        db.delete(row)
        db.commit()
        return None