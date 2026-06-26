"""
Drift-detector PACK register / activate endpoints.

The CRUD scaffold already exposes plain ``/api/v1/detector_packs/`` (list /
get / create / update / delete). This router adds the two operations the
scaffold can't express:

    POST /api/v1/detector_packs/register      (multipart upload)
    POST /api/v1/detector_packs/{id}/activate (pin/deploy)

``register`` is the "add / install a pack" action: it accepts a
``drift_detectors/`` archive (the slim pip package, ~168 KB), validates it,
computes a sha256, extracts the version, PARSES each detector's
``metadata.yaml`` and stores that list ON THE PACK ROW (read-only listing --
name/kind/description/params per detector), stores the slim archive on disk
for provenance, and records the pack here. CRUD here is over the PACK (zip):
add (register), update (re-register same name+version), delete, activate.
It deliberately does NOT write the ``drift_detectors`` catalog -- uploading a
pack lists its detectors, it does not edit them.

Execution stays with the Airflow DAG: it runs the pinned (``is_active``) pack
server-side and writes ``drift_results``. FermOps never imports detector code.
"""

from __future__ import annotations

import hashlib
import io
import logging
import os
import re
import zipfile
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

import yaml
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from model_registry.api.core.database import get_db
from model_registry.api.core.dependencies import require_permission_resource
from model_registry.api.models.detector_pack import DetectorPack

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/detector_packs", tags=["Detector packs"])

# Where stored slim archives live. Override with DETECTOR_PACKS_DIR.
PACKS_DIR = os.environ.get(
    "DETECTOR_PACKS_DIR",
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "detector_packs_store"),
)

_VALID_KINDS = {"univariate", "multivariate", "model_based"}


# ----------------------------------------------------------------- parsing
def _extract_version(members: dict[str, bytes]) -> str:
    """Best-effort pack version: pyproject [project].version, else __version__."""
    for path, raw in members.items():
        if path.endswith("pyproject.toml"):
            m = re.search(
                r'(?m)^\s*version\s*=\s*["\']([^"\']+)["\']',
                raw.decode("utf-8", "ignore"),
            )
            if m:
                return m.group(1)
    for path, raw in members.items():
        if path.endswith("drift_detectors/__init__.py"):
            m = re.search(
                r'__version__\s*=\s*["\']([^"\']+)["\']', raw.decode("utf-8", "ignore")
            )
            if m:
                return m.group(1)
    return "0.0.0+unknown"


def _parse_metadata(members: dict[str, bytes]) -> list[dict[str, Any]]:
    """Turn each detector's metadata.yaml into a catalog row.

    A folder counts as a detector only if it ships BOTH ``metadata.yaml`` and
    a sibling ``detector.py`` (this excludes helper catalogues like
    ``disagreement_metrics`` that carry metadata but aren't detectors).
    detector_id = folder name (matches drift_detectors.detector_id + the
    06 seed). Mirrors the seed's column mapping.
    """
    has_detector_py = {
        os.path.dirname(p)
        for p in members
        if p.endswith("/detector.py") or p.endswith("\\detector.py")
    }
    rows: list[dict[str, Any]] = []
    for path, raw in members.items():
        if not path.endswith("metadata.yaml"):
            continue
        folder = os.path.dirname(path)
        if folder not in has_detector_py:
            continue
        try:
            meta = yaml.safe_load(raw.decode("utf-8", "ignore")) or {}
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning("skipping unparseable metadata.yaml %s: %s", path, exc)
            continue
        detector_id = os.path.basename(folder)
        kind = str(meta.get("type", "")).strip().lower() or "univariate"
        params_meta = meta.get("parameters") or {}
        params = {}
        if isinstance(params_meta, dict):
            for k, v in params_meta.items():
                params[k] = v.get("description") if isinstance(v, dict) else str(v)
        rows.append(
            {
                "detector_id": detector_id,
                "name": meta.get("name") or detector_id,
                "kind": kind if kind in _VALID_KINDS else kind,
                "description": (meta.get("description") or "").strip() or None,
                "params": params,
            }
        )
    return rows


def _read_pack(blob: bytes) -> tuple[dict[str, bytes], str, list[dict[str, Any]]]:
    """Validate the archive; return (members, version, catalog_rows)."""
    try:
        zf = zipfile.ZipFile(io.BytesIO(blob))
    except zipfile.BadZipFile:
        raise HTTPException(400, "Uploaded file is not a valid .zip archive")
    members = {n: zf.read(n) for n in zf.namelist() if not n.endswith("/")}
    if not any("drift_detectors/" in p.replace("\\", "/") for p in members):
        raise HTTPException(400, "Archive does not contain a drift_detectors/ package")
    version = _extract_version(members)
    rows = _parse_metadata(members)
    if not rows:
        raise HTTPException(
            400, "No detectors found (need folders with metadata.yaml + detector.py)"
        )
    return members, version, rows


def _build_slim_archive(members: dict[str, bytes]) -> bytes:
    """Re-zip only the drift_detectors/ package (drop benchmarks/use_cases/tests)."""
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        for path, raw in members.items():
            norm = path.replace("\\", "/")
            idx = norm.find("drift_detectors/")
            if idx == -1:
                continue
            zf.writestr(norm[idx:], raw)
    return out.getvalue()


def _row_to_dict(row: DetectorPack) -> dict[str, Any]:
    return {
        "id": str(row.id),
        "name": row.name,
        "version": row.version,
        "source": row.source,
        "checksum": row.checksum,
        "storage_path": row.storage_path,
        "detector_count": row.detector_count,
        "detectors": row.detectors,
        "is_active": row.is_active,
        "notes": row.notes,
        "created_by": str(row.created_by) if row.created_by else None,
        "created_at": row.created_at.isoformat() if row.created_at else None,
    }


# ----------------------------------------------------------------- routes
@router.post("/register")
def register_pack(
    file: UploadFile = File(...),
    name: str | None = Form(None),
    notes: str | None = Form(None),
    activate: bool = Form(False),
    db: Session = Depends(get_db),
    user=Depends(require_permission_resource("detector_packs:write", "detector_packs")),
):
    """Validate + ingest an uploaded drift_detectors pack, store it, record it."""
    blob = file.file.read()
    if not blob:
        raise HTTPException(400, "Empty upload")

    members, version, rows = _read_pack(blob)
    pack_name = (name or "stamm-drift-detectors").strip()

    # Slim archive (drift_detectors/ only) + checksum for provenance.
    slim = _build_slim_archive(members)
    checksum = hashlib.sha256(slim).hexdigest()
    os.makedirs(PACKS_DIR, exist_ok=True)
    fname = f"{pack_name}-{version}-{checksum[:8]}.zip"
    storage_path = os.path.join(PACKS_DIR, fname)
    with open(storage_path, "wb") as fh:
        fh.write(slim)

    # List-only: keep the full detector metadata WITH the pack. We do NOT
    # touch the drift_detectors catalog -- registering a pack adds/updates the
    # zip and lists what's inside it, nothing more.
    detectors = [
        {
            "detector_id": r["detector_id"],
            "name": r["name"],
            "kind": r["kind"],
            "description": r["description"],
            "params": r["params"],
        }
        for r in rows
    ]

    # Upsert the pack row (unique on name+version).
    pack = (
        db.query(DetectorPack)
        .filter(DetectorPack.name == pack_name, DetectorPack.version == version)
        .first()
    )
    created_by = getattr(user, "id", None)
    if pack:
        pack.checksum = checksum
        pack.storage_path = storage_path
        pack.detector_count = len(detectors)
        pack.detectors = detectors
        pack.notes = notes if notes is not None else pack.notes
        pack.source = "upload"
    else:
        pack = DetectorPack(
            id=uuid4(),
            name=pack_name,
            version=version,
            source="upload",
            checksum=checksum,
            storage_path=storage_path,
            detector_count=len(detectors),
            detectors=detectors,
            is_active=False,
            notes=notes,
            created_by=created_by,
            created_at=datetime.utcnow(),
        )
        db.add(pack)
    db.flush()

    if activate:
        _activate(db, pack)

    db.commit()
    db.refresh(pack)
    logger.info(
        "Registered detector pack %s v%s (%d detectors, active=%s)",
        pack_name,
        version,
        len(detectors),
        pack.is_active,
    )
    return {
        "pack": _row_to_dict(pack),
        "detectors": detectors,
        "detector_count": len(detectors),
    }


def _activate(db: Session, pack: DetectorPack) -> None:
    """Pin one pack per name: deactivate siblings, activate this one."""
    db.query(DetectorPack).filter(
        DetectorPack.name == pack.name,
        DetectorPack.id != pack.id,
        DetectorPack.is_active.is_(True),
    ).update({DetectorPack.is_active: False}, synchronize_session=False)
    pack.is_active = True


@router.post("/{pack_id}/activate")
def activate_pack(
    pack_id: str,
    db: Session = Depends(get_db),
    user=Depends(require_permission_resource("detector_packs:edit", "detector_packs")),
):
    """Deploy/pin a pack: mark it active (one active pack per name)."""
    try:
        pid = UUID(pack_id)
    except ValueError:
        raise HTTPException(400, f"invalid UUID: {pack_id}")
    pack = db.query(DetectorPack).filter(DetectorPack.id == pid).first()
    if not pack:
        raise HTTPException(404, "detector pack not found")
    _activate(db, pack)
    db.commit()
    db.refresh(pack)
    return {"pack": _row_to_dict(pack)}
